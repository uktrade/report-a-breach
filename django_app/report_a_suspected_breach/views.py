import logging
import uuid
from typing import Any

# from core.decorators import cached_classproperty
from core.document_storage import TemporaryDocumentStorage  # PermanentDocumentStorage,

# from core.templatetags.get_wizard_step_url import get_wizard_step_url
from core.utils import is_ajax
from core.views import BaseFormView
from django.conf import settings
from django.core.cache import cache

# from django.db import transaction
from django.forms import Form
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django_ratelimit.decorators import ratelimit
from feedback.forms import FeedbackForm
from utils.breach_report import get_breach_context_data

# from utils.companies_house import get_formatted_address
from utils.notifier import verify_email
from utils.s3 import (
    generate_presigned_url,
    get_all_session_files,
    get_user_uploaded_files,
)

# from .choices import TypeOfRelationshipChoices
# from .exceptions import EmailNotVerifiedException
from .forms import (
    EmailForm,
    EmailVerifyForm,
    NameAndBusinessYouWorkForForm,
    NameForm,
    StartForm,
    SummaryForm,
    UploadDocumentsForm,
    ZeroEndUsersForm,
)
from .models import Breach

logger = logging.getLogger(__name__)


class StartView(BaseFormView):
    template_name = "report_a_suspected_breach/generic_nonwizard_form_step.html"
    form_class = StartForm
    success_url = reverse_lazy("report_a_suspected_breach:email")

    def form_valid(self, form: StartForm) -> HttpResponse:
        self.request.session["completed_steps"] = {
            "reporter_professional_relationship": form.cleaned_data["reporter_professional_relationship"]
        }
        return super().form_valid(form)


class EmailView(BaseFormView):
    template_name = "report_a_suspected_breach/generic_nonwizard_form_step.html"
    form_class = EmailForm
    success_url = reverse_lazy("report_a_suspected_breach:email_verify")

    def form_valid(self, form: EmailForm) -> HttpResponse:
        reporter_email_address = form.cleaned_data.get("reporter_email_address")
        self.request.session["completed_steps"]["reporter_email_address"] = reporter_email_address
        verify_email(reporter_email_address, self.request)
        return super().form_valid(form)


class CompleteView(TemplateView):
    template_name = "report_a_suspected_breach/complete.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        self.breach = Breach.objects.filter(reference=self.request.session.get("reference_id")).first()
        context = get_breach_context_data(context, self.breach)
        context["feedback_form"] = FeedbackForm()

        return context


class UploadDocumentsView(FormView):
    """View for uploading documents. This view is used in the wizard flow, but can also be accessed directly.

    Accepts both Ajax and non-Ajax requests, to accommodate both JS and non-JS users respectively."""

    form_class = UploadDocumentsForm
    template_name = "report_a_suspected_breach/form_steps/upload_documents.html"
    file_storage = TemporaryDocumentStorage()

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Retrieve the already uploaded files from the session storage and add them to the context."""
        context = super().get_context_data(**kwargs)
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            context["session_files"] = session_files
        return context

    def form_valid(self, form: Form) -> HttpResponse:
        """Loop through the files and save them to the temporary storage. If the request is Ajax, return a JsonResponse.

        If the request is not Ajax, redirect to the summary page (the next step in the form)."""
        for temporary_file in form.cleaned_data["document"]:
            # adding the file name to the cache, so we can retrieve it later and confirm they uploaded it
            # we add a unique identifier to the key, so we do not overwrite previous uploads
            redis_cache_key = f"{self.request.session.session_key}{uuid.uuid4()}"
            cache.set(redis_cache_key, temporary_file.original_name)

            if is_ajax(self.request):
                # if it's an AJAX request, then files are sent to this view one at a time, so we can return a response
                # immediately, and not at the end of the for-loop
                return JsonResponse(
                    {
                        "success": True,
                        "file_name": temporary_file.original_name,
                    },
                    status=201,
                )
        if is_ajax(self.request):
            return JsonResponse({"success": True}, status=200)
        else:
            return redirect(reverse_lazy("report_a_suspected_breach:tell_us_about_the_suspected_breach"))

    def form_invalid(self, form: Form) -> HttpResponse:
        if is_ajax(self.request):
            return JsonResponse(
                {"success": False, "error": form.errors["document"][0], "file_name": self.request.FILES["document"].name},
                status=200,
            )
        else:
            return super().form_invalid(form)


class DeleteDocumentsView(View):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        if file_name := self.request.GET.get("file_name"):
            full_file_path = f"{self.request.session.session_key}/{file_name}"
            TemporaryDocumentStorage().delete(full_file_path)

            if is_ajax(self.request):
                return JsonResponse({"success": True}, status=200)
            else:
                return redirect(reverse("report_a_suspected_breach:upload_documents"))

        if is_ajax(self.request):
            return JsonResponse({"success": False}, status=400)
        else:
            return redirect(reverse("report_a_suspected_breach:upload_documents"))


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class RequestVerifyCodeView(BaseFormView):
    form_class = SummaryForm
    template_name = "report_a_suspected_breach/form_steps/request_verify_code.html"
    success_url = reverse_lazy("report_a_suspected_breach:email_verify")

    def form_valid(self, form: SummaryForm) -> HttpResponse:
        reporter_email_address = self.request.session["completed_steps"]["reporter_email_address"]
        if getattr(self.request, "limited", False):
            logger.warning(f"User has been rate-limited: {reporter_email_address}")
            return self.form_invalid(form)
        verify_email(reporter_email_address, self.request)
        return super().form_valid(form)


@method_decorator(ratelimit(key="ip", rate=settings.RATELIMIT, method="POST", block=False), name="post")
class EmailVerifyView(BaseFormView):
    form_class = EmailVerifyForm
    template_name = "report_a_suspected_breach/generic_nonwizard_form_step.html"

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super(EmailVerifyView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if form_h1_header := getattr(EmailVerifyForm, "form_h1_header"):
            context["form_h1_header"] = form_h1_header
        return context

    def get_success_url(self) -> str:
        relationship_data = self.request.session["completed_steps"].get("reporter_professional_relationship")
        if relationship_data in ("owner", "acting"):
            return reverse_lazy("report_a_suspected_breach:name")
        elif relationship_data in ("third_party", "no_professional_relationship"):
            return reverse_lazy("report_a_suspected_breach:name_and_business_you_work_for")
        else:
            return reverse_lazy("report_a_suspected_breach:landing")

    def form_valid(self, form: EmailVerifyForm) -> HttpResponse:
        form.verification_object.verified = True
        form.verification_object.save()
        self.request.session["completed_steps"].update({"email_verify": True})
        return super().form_valid(form)


class NameView(BaseFormView):
    form_class = NameForm
    template_name = "report_a_suspected_breach/generic_nonwizard_form_step.html"

    def get_success_url(self) -> str:
        if self.request.session.get("redirect") == "summary" or self.request.GET.get("redirect", "") == "summary":
            return reverse_lazy("report_a_suspected_breach:summary")
        return reverse_lazy("report_a_suspected_breach:landing")

    def form_valid(self, form: NameForm) -> HttpResponse:
        name = form.cleaned_data["reporter_full_name"]
        self.request.session["completed_steps"]["name"] = name
        return super().form_valid(form)


class NameAndBusinessYouWorkForView(BaseFormView):
    form_class = NameAndBusinessYouWorkForForm
    template_name = "report_a_suspected_breach/generic_nonwizard_form_step.html"

    def get_success_url(self) -> str:
        if self.request.session.get("redirect") == "summary" or self.request.GET.get("redirect", "") == "summary":
            return reverse_lazy("report_a_suspected_breach:summary")
        return reverse_lazy("report_a_suspected_breach:landing")

    def form_valid(self, form: NameAndBusinessYouWorkForForm) -> HttpResponse:
        name = form.cleaned_data["reporter_full_name"]
        business_you_work_for = form.cleaned_data["reporter_name_of_business_you_work_for"]
        self.request.session["completed_steps"]["name_and_business_you_work_for"] = [name, business_you_work_for]
        return super().form_valid(form)


class DownloadDocumentView(View):
    http_method_names = ["get"]

    def get(self, *args: object, file_name, **kwargs: object) -> HttpResponse:
        user_uploaded_files = get_user_uploaded_files(self.request.session)

        if file_name in user_uploaded_files:
            logger.info(f"User is downloading file: {file_name}")
            session_keyed_file_name = f"{self.request.session.session_key}/{file_name}"
            file_url = generate_presigned_url(TemporaryDocumentStorage(), session_keyed_file_name)
            return redirect(file_url)

        raise Http404()


class DeleteEndUserView(View):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        redirect_to = redirect(reverse_lazy("report_a_suspected_breach:step", kwargs={"step": "end_user_added"}))
        if end_user_uuid := self.request.POST.get("end_user_uuid"):
            end_users = self.request.session.pop("end_users", None)
            end_users.pop(end_user_uuid, None)
            self.request.session["end_users"] = end_users
            self.request.session.modified = True
            if len(end_users) == 0:
                redirect_to = redirect(reverse_lazy("report_a_suspected_breach:zero_end_users"))
        return redirect_to


class ZeroEndUsersView(FormView):
    form_class = ZeroEndUsersForm
    template_name = "report_a_suspected_breach/generic_nonwizard_form_step.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if form_h1_header := getattr(ZeroEndUsersForm, "form_h1_header"):
            context["form_h1_header"] = form_h1_header
        return context

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        add_end_user = self.form.cleaned_data["do_you_want_to_add_an_end_user"]
        if add_end_user:
            if self.request.session.get("made_available_journey"):
                return (
                    f"{reverse_lazy('report_a_suspected_breach:where_were_the_goods_made_available_to')}?add_another_end_user=yes"
                )

            else:
                return f"{reverse_lazy('report_a_suspected_breach:where_were_the_goods_supplied_to')}?add_another_end_user=yes"

        else:
            # TODO: more wizard logic to remove
            return reverse_lazy(
                "report_a_suspected_breach:step", kwargs={"step": "were_there_other_addresses_in_the_supply_chain"}
            )


class TaskView(TemplateView):
    template_name = "report_a_suspected_breach/tasklist.html"

    tasklist = {
        "Your Details": {
            "steps": ["start", "email", "email_verify"],
            "success_steps": ["name", "name_and_business_you_work_for"],
        },
        "About the person or business you're reporting": {
            "steps": [
                "are_you_reporting_a_business_on_companies_house",
                "do_you_know_the_registered_company_number",
                "manual_companies_house_input",
                "where_is_the_address_of_the_business_or_person",
            ],
            "success_steps": ["check_company_details", "business_or_person_details"],
            "hint_text": "Contact details",
        },
        "Overview of the suspected breach": {
            "steps": [
                "when_did_you_first_suspect",
                "which_sanctions_regime",
            ],
            "success_steps": ["what_were_the_goods"],
            "hint_text": "Which sanctions were breached, and what were the goods or services",
        },
        "The supply chain": {
            "steps": [
                "where_were_the_goods_supplied_from",
                "about_the_supplier",
                "where_were_the_goods_made_available_from",
                "where_were_the_goods_supplied_to",
                "where_were_the_goods_made_available_to",
                "about_the_end_user",
            ],
            "success_steps": ["were_there_other_addresses_in_the_supply_chain"],
            "hint_text": "Contact details for the supplier, end-user and anyone else in the supply chain",
        },
        "Sanctions breach details": {
            "steps": ["upload_documents"],
            "success_steps": ["tell_us_about_the_suspected_breach"],
            "hint_text": "Upload documents and give any additional information",
        },
    }

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        previous_task_completed = False
        context["tasklist"] = {}

        # TODO: can likely simplify
        # TODO: need to add a complete value to the top level tasklist
        for task in self.tasklist:
            context["tasklist"][task] = {}
            if not previous_task_completed and task != "Your Details":
                context["tasklist"][task]["status"] = "Cannot start yet"
            elif task == "Your Details":
                context["tasklist"][task]["status"] = "Not yet started"
            elif previous_task_completed:
                context["tasklist"][task]["status"] = "Not yet started"

            if self.tasklist[task].get("hint_text", ""):
                context["tasklist"][task]["hint_text"] = self.tasklist[task]["hint_text"]
            context["tasklist"][task]["underscored_task_name"] = task.lower().replace(" ", "_")
            context["tasklist"][task]["start_url"] = self.tasklist[task]["steps"][0]
            context["tasklist"][task]["name"] = task

            # Check if the task has been completed
            success = False
            for success_step in self.tasklist[task]["success_steps"]:
                if success_step in self.request.session.get("completed_steps", {}):
                    context["tasklist"][task]["status"] = "Completed"
                    success = True
                    previous_task_completed = True

            if not success and task != "Your Details":
                if not previous_task_completed:
                    context["tasklist"][task]["can_start"] = False
                else:
                    context["tasklist"][task]["can_start"] = True
                previous_task_completed = False
            elif not success and task == "Your Details":
                context["tasklist"][task]["can_start"] = True

        return context
