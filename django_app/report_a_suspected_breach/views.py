import logging
import uuid
from typing import Any

from core.decorators import cached_classproperty
from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage
from core.templatetags.get_wizard_step_url import get_wizard_step_url
from core.utils import is_ajax
from core.views import BaseWizardView
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.forms import Form
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from feedback.forms import FeedbackForm
from utils.breach_report import get_breach_context_data
from utils.companies_house import get_formatted_address
from utils.notifier import verify_email
from utils.s3 import (
    delete_session_files,
    generate_presigned_url,
    get_all_session_files,
    get_user_uploaded_files,
)

from .choices import TypeOfRelationshipChoices
from .forms import EmailVerifyForm, SummaryForm, UploadDocumentsForm
from .models import Breach, PersonOrCompany, ReporterEmailVerification, SanctionsRegime
from .tasklist import (
    AboutThePersonOrBusinessTask,
    OverviewOfTheSuspectedBreachTask,
    SanctionsBreachDetailsTask,
    SummaryAndDeclaration,
    TheSupplyChainTask,
    YourDetailsTask,
    get_blocked_steps,
    get_tasklist,
)

logger = logging.getLogger(__name__)


class ReportABreachWizardView(BaseWizardView):
    template_names_lookup = {
        "summary": "report_a_suspected_breach/form_steps/summary.html",
        "check_company_details": "report_a_suspected_breach/form_steps/check_company_details.html",
        "end_user_added": "report_a_suspected_breach/form_steps/end_user_added.html",
        "declaration": "report_a_suspected_breach/form_steps/declaration.html",
        "upload_documents": "report_a_suspected_breach/form_steps/upload_documents.html",
    }
    template_name = "report_a_suspected_breach/generic_form_step.html"
    storage_name = "report_a_suspected_breach.session.SessionStorage"
    file_storage = TemporaryDocumentStorage()

    @cached_classproperty
    def form_list(cls) -> list[tuple[Any, Any]]:
        task_list = (
            YourDetailsTask,
            AboutThePersonOrBusinessTask,
            OverviewOfTheSuspectedBreachTask,
            TheSupplyChainTask,
            SanctionsBreachDetailsTask,
            SummaryAndDeclaration,
        )
        unpacked = []
        for task in task_list:
            for step_name, step_form in task.form_steps.items():
                unpacked.append((step_name, step_form))

        return unpacked

    def get_context_data(self, form: Form, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(form, **kwargs)
        context["back_button_link"] = self.get_step_url(self.steps.prev)
        return context

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if "reset" in self.request.GET:
            for step_name, _ in self.form_list.items():
                # clearing the lru_cache for get_cleaned_data_for_step
                if self.get_cleaned_data_for_step.has(step_name):
                    self.get_cleaned_data_for_step.delete(step_name)
            self.storage.reset()
            self.storage.current_step = self.steps.first

        if current_step := kwargs.get("step"):
            if is_step_blocked(self, request, current_step):
                raise Http404("This page is blocked")

        if request.resolver_match.url_name == "about_the_end_user":
            # we want to add another end-user, we need to ask the user if the new end-user is in the UK or not
            if "end_user_uuid" not in self.request.resolver_match.kwargs:
                default_redirect = "where_were_the_goods_supplied_to"
                if self.request.session.get("made_available_journey"):
                    default_redirect = "where_were_the_goods_made_available_to"
                self.storage.current_step = default_redirect
                kwargs["step"] = default_redirect
                return super().get(request, *args, **kwargs)
            else:
                # we're trying to edit an existing end-user, so we need to load the form with the existing data
                self.storage.current_step = "about_the_end_user"
                return super().get(request, *args, step="about_the_end_user", **kwargs)

        # before we initialise the tasklist, we need to make sure the current_step is correct
        if step_url := kwargs.get("step", None):
            if step_url in self.get_form_list():
                self.storage.current_step = step_url

        if self.storage.current_step == "upload_documents":
            return redirect(reverse("report_a_suspected_breach:upload_documents"))

        if self.storage.current_step == "verify":
            return redirect(reverse("report_a_suspected_breach:email_verify"))

        # check if the user has completed a task, if so, redirect them to the tasklist
        # the exception to this is if the user wants to explicitly start the next task, in which case we should let them
        # or, if they're trying to change their answers from the summary page
        self.tasklist = get_tasklist(self)
        if (
            not request.GET.get("start", "") == "true"
            and not request.session.get("redirect") == "summary"
            and not request.GET.get("redirect", "") == "summary"
            and self.tasklist.should_show_task_list_page()
        ):
            return render(request, "report_a_suspected_breach/tasklist.html", context={"tasklist": self.tasklist, "view": self})

        return super().get(request, *args, **kwargs)

    def get_step_url(self, step: str) -> str:
        if step == "about_the_end_user" and "end_user_uuid" in self.kwargs:
            return reverse(
                "report_a_suspected_breach:about_the_end_user",
                kwargs={"end_user_uuid": self.kwargs["end_user_uuid"]},
            )

        if step == "where_were_the_goods_supplied_to" and "end_user_uuid" in self.kwargs:
            return reverse(
                "report_a_suspected_breach:where_were_the_goods_supplied_to",
                kwargs={"end_user_uuid": self.kwargs["end_user_uuid"]},
            )

        if step == "where_were_the_goods_made_available_to" and "end_user_uuid" in self.kwargs:
            return reverse(
                "report_a_suspected_breach:where_were_the_goods_made_available_to",
                kwargs={"end_user_uuid": self.kwargs["end_user_uuid"]},
            )
        return super().get_step_url(step)

    def render_next_step(self, form: Form, **kwargs: object) -> HttpResponse:
        if self.steps.current == "end_user_added" and form.cleaned_data["do_you_want_to_add_another_end_user"]:
            default_path = "where_were_the_goods_supplied_to"
            if self.request.session.get("made_available_journey"):
                default_path = "where_were_the_goods_made_available_to"

            # we want to redirect them to 'where is the end user' page, but pass another query parameter to indicate that they
            # know about another end-user, so we can remove the last option 'I don't know' from the list of options
            return redirect(f"{self.get_step_url(default_path)}?add_another_end_user=yes")

        if self.steps.current == "where_were_the_goods_made_available_from":
            # we don't want to call super() here as that appears to be calling the next item in the form list
            # rather than applying the condition logic
            if form.cleaned_data["where_were_the_goods_made_available_from"] in ["different_uk_address", "outside_the_uk"]:
                return redirect(self.get_step_url("about_the_supplier"))
            elif form.cleaned_data["where_were_the_goods_made_available_from"] in ["same_address", "i_do_not_know"]:
                return redirect(self.get_step_url("where_were_the_goods_made_available_to"))

        return super().render_next_step(form, **kwargs)

    def get_summary_context_data(self, form: Form, context: dict[str, Any]) -> dict[str, Any]:
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""

        # we're importing these methods here to avoid circular imports
        from .form_step_conditions import (
            show_check_company_details_page_condition,
            show_name_and_business_you_work_for_page,
        )

        cleaned_data = self.get_all_cleaned_data()
        context["form_data"] = cleaned_data
        context["is_company_obtained_from_companies_house"] = show_check_company_details_page_condition(self)
        context["is_third_party_relationship"] = show_name_and_business_you_work_for_page(self)
        context["is_made_available_journey"] = self.request.session.get("made_available_journey")
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            context["form_data"]["session_files"] = session_files
        if end_users := self.request.session.get("end_users", None):
            context["form_data"]["end_users"] = end_users

        if (
            self.get_cleaned_data_for_step("where_were_the_goods_supplied_from").get("where_were_the_goods_supplied_from")
            == "same_address"
        ):
            if show_check_company_details_page_condition(self):
                registered_company = context["form_data"]["do_you_know_the_registered_company_number"]
                context["form_data"]["about_the_supplier"] = {}
                context["form_data"]["about_the_supplier"]["name"] = registered_company["registered_company_name"]
                context["form_data"]["about_the_supplier"]["readable_address"] = registered_company["registered_office_address"]
                context["form_data"]["about_the_supplier"]["country"] = "GB"
            else:
                context["form_data"]["about_the_supplier"] = context["form_data"]["business_or_person_details"]
        return context

    def process_start_step(self, form: Form) -> QueryDict:
        self.request.session["reporter_professional_relationship"] = form.cleaned_data["reporter_professional_relationship"]
        self.request.session.modified = True

        return self.get_form_step_data(form)

    def process_are_you_reporting_a_business_on_companies_house_step(self, form: Form) -> QueryDict:
        """We want to clear the company details from the session if the user selects anything but 'yes', if they do
        select 'yes' then we want to delete the step data for the next step(s) in the chain of conditionals."""
        if form.cleaned_data["business_registered_on_companies_house"] != "yes":
            self.request.session.pop("company_details", None)
            self.request.session.modified = True
        else:
            self.storage.delete_step_data("where_is_the_address_of_the_business_or_person", "business_or_person_details")

        return self.get_form_step_data(form)

    def process_about_the_end_user_step(self, form: Form) -> QueryDict:
        current_end_users = self.request.session.get("end_users", {})

        end_user_uuid = self.kwargs.get("end_user_uuid", str(uuid.uuid4()))
        # want to save both the cleaned data (for rendering to the user in the summary page) and the dirty data
        # (for re-instantiating the form in the case of a user wanting to change their input)
        current_end_users[end_user_uuid] = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["end_users"] = current_end_users
        self.request.session.modified = True
        return self.get_form_step_data(form)

    def process_do_you_know_the_registered_company_number_step(self, form: Form) -> QueryDict:
        self.request.session.pop("company_details", None)
        self.request.session.modified = True

        if form.cleaned_data.get("do_you_know_the_registered_company_number") == "yes":
            self.request.session["company_details"] = form.cleaned_data

        return self.get_form_step_data(form)

    def process_email_step(self, form: Form) -> QueryDict:
        reporter_email_address = form.cleaned_data.get("reporter_email_address")
        self.request.session["reporter_email_address"] = reporter_email_address
        self.request.session.modified = True

        verify_email(reporter_email_address, self.request)
        return self.get_form_step_data(form)

    def get_form_kwargs(self, step: str | None) -> dict[str, Any]:
        kwargs = super().get_form_kwargs(step)
        kwargs["request"] = self.request

        if step == "business_or_person_details":
            where_is_the_address = (
                self.get_cleaned_data_for_step("where_is_the_address_of_the_business_or_person").get("where_is_the_address")
                == "in_the_uk"
            )
            do_you_know_the_registered_company_number = (
                self.get_cleaned_data_for_step("do_you_know_the_registered_company_number").get(
                    "do_you_know_the_registered_company_number"
                )
                == "no"
            )
            if where_is_the_address or do_you_know_the_registered_company_number:
                kwargs["is_uk_address"] = "in_the_uk"

        if step == "about_the_supplier":
            where_were_the_goods_supplied_from = (self.get_cleaned_data_for_step("where_were_the_goods_supplied_from") or {}).get(
                "where_were_the_goods_supplied_from", ""
            )
            if where_were_the_goods_supplied_from:
                is_uk_address = where_were_the_goods_supplied_from == "different_uk_address"
                kwargs["is_uk_address"] = is_uk_address
            where_were_the_goods_made_available_from = (
                self.get_cleaned_data_for_step("where_were_the_goods_made_available_from") or {}
            ).get("where_were_the_goods_made_available_from", "")
            if where_were_the_goods_made_available_from:
                is_uk_address = where_were_the_goods_made_available_from == "different_uk_address"
                kwargs["is_uk_address"] = is_uk_address

        if step == "about_the_end_user":
            where_were_the_goods_supplied_to = (self.get_cleaned_data_for_step("where_were_the_goods_supplied_to") or {}).get(
                "where_were_the_goods_supplied_to", ""
            )
            if where_were_the_goods_supplied_to:
                is_uk_address = where_were_the_goods_supplied_to == "in_the_uk"
                kwargs["is_uk_address"] = is_uk_address

            where_were_the_goods_made_available_to = (
                self.get_cleaned_data_for_step("where_were_the_goods_made_available_to") or {}
            ).get("where_were_the_goods_made_available_to", "")
            if where_were_the_goods_made_available_to:
                is_uk_address = where_were_the_goods_made_available_to == "in_the_uk"
                kwargs["is_uk_address"] = is_uk_address

        if step in (
            "where_were_the_goods_supplied_from",
            "where_were_the_goods_made_available_from",
        ):
            from .form_step_conditions import show_check_company_details_page_condition

            obtained_from_companies_house = show_check_company_details_page_condition(self)
            if obtained_from_companies_house:
                address_string = self.get_cleaned_data_for_step("do_you_know_the_registered_company_number").get(
                    "registered_office_address"
                )
            else:
                address_string = get_formatted_address(self.get_cleaned_data_for_step("business_or_person_details"))

            kwargs["address_string"] = address_string

        return kwargs

    def store_documents_in_s3(self, breach_id: str) -> None:
        """
        Copies documents from the default temporary storage to permanent storage on s3, then deletes from temporary storage
        """
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            permanent_storage_bucket = PermanentDocumentStorage()
            for object_key in session_files.keys():
                try:
                    permanent_storage_bucket.bucket.meta.client.copy(
                        CopySource={
                            "Bucket": settings.TEMPORARY_S3_BUCKET_NAME,
                            "Key": f"{self.request.session.session_key}/{object_key}",
                        },
                        Bucket=settings.PERMANENT_S3_BUCKET_NAME,
                        Key=f"{breach_id}/{object_key}",
                        SourceClient=self.file_storage.bucket.meta.client,
                    )
                except Exception:
                    # todo - AccessDenied when copying from temporary to permanent bucket when deployed - investigate
                    pass
                else:
                    delete_session_files(TemporaryDocumentStorage(), self.request.session)

    def save_person_or_company_to_db(
        self, breach: Breach, person_or_company: dict[str, str], relationship: TypeOfRelationshipChoices
    ) -> None:
        new_business_or_person_details = PersonOrCompany.objects.create(
            name=person_or_company.get("name", ""),
            name_of_business=person_or_company.get("name_of_business"),
            website=person_or_company.get("website"),
            email=person_or_company.get("email"),
            address_line_1=person_or_company.get("address_line_1"),
            address_line_2=person_or_company.get("address_line_2"),
            address_line_3=person_or_company.get("address_line_3"),
            address_line_4=person_or_company.get("address_line_4"),
            town_or_city=person_or_company.get("town_or_city"),
            country=person_or_company.get("country"),
            county=person_or_company.get("county"),
            postal_code=person_or_company.get("postal_code", ""),
            additional_contact_details=person_or_company.get("additional_contact_details"),
            breach=breach,
            type_of_relationship=relationship,
        )
        new_business_or_person_details.save()

    def save_companies_house_company_to_db(
        self, breach: Breach, companies_house_company: dict[str, str], relationship: TypeOfRelationshipChoices
    ) -> None:
        new_companies_house_company = PersonOrCompany.objects.create(
            name=companies_house_company.get("registered_company_name"),
            country="GB",
            registered_company_number=companies_house_company.get("registered_company_number"),
            registered_office_address=companies_house_company.get("registered_office_address"),
            breach=breach,
            type_of_relationship=relationship,
        )
        new_companies_house_company.save()

    def done(self, form_list: list[str], **kwargs: object) -> HttpResponse:
        cleaned_data = self.get_all_cleaned_data()
        # we're importing these methods here to avoid circular imports
        from .form_step_conditions import (
            show_about_the_supplier_page,
            show_check_company_details_page_condition,
            show_name_and_business_you_work_for_page,
        )

        if show_name_and_business_you_work_for_page(self):
            reporter_full_name = cleaned_data["name_and_business_you_work_for"]["reporter_full_name"]
            reporter_name_of_business_you_work_for = cleaned_data["name_and_business_you_work_for"][
                "reporter_name_of_business_you_work_for"
            ]
        else:
            reporter_full_name = cleaned_data["name"]["reporter_full_name"]
            business_or_person_details_step = cleaned_data.get("business_or_person_details", {})
            reporter_name_of_business_you_work_for = business_or_person_details_step.get("name", "")

        with transaction.atomic():
            reporter_email_verification = ReporterEmailVerification.objects.filter(
                reporter_session=self.request.session.session_key
            ).latest("date_created")
            # Save Breach to Database
            new_breach = Breach.objects.create(
                reporter_professional_relationship=cleaned_data["start"]["reporter_professional_relationship"],
                reporter_email_address=cleaned_data["email"]["reporter_email_address"],
                reporter_email_verification=reporter_email_verification,
                reporter_full_name=reporter_full_name,
                reporter_name_of_business_you_work_for=reporter_name_of_business_you_work_for,
                when_did_you_first_suspect=cleaned_data["when_did_you_first_suspect"]["when_did_you_first_suspect"],
                is_the_date_accurate=cleaned_data["when_did_you_first_suspect"]["is_the_date_accurate"],
                what_were_the_goods=cleaned_data["what_were_the_goods"]["what_were_the_goods"],
                where_were_the_goods_supplied_from=cleaned_data["where_were_the_goods_supplied_from"][
                    "where_were_the_goods_supplied_from"
                ],
                were_there_other_addresses_in_the_supply_chain=cleaned_data["were_there_other_addresses_in_the_supply_chain"][
                    "were_there_other_addresses_in_the_supply_chain"
                ],
                other_addresses_in_the_supply_chain=cleaned_data["were_there_other_addresses_in_the_supply_chain"][
                    "other_addresses_in_the_supply_chain"
                ],
                tell_us_about_the_suspected_breach=cleaned_data["tell_us_about_the_suspected_breach"][
                    "tell_us_about_the_suspected_breach"
                ],
            )
            if declared_sanctions := cleaned_data["which_sanctions_regime"]["which_sanctions_regime"]:
                new_breach.unknown_sanctions_regime = "Unknown Regime" in declared_sanctions
                new_breach.other_sanctions_regime = "Other Regime" in declared_sanctions
                sanctions_regimes = SanctionsRegime.objects.filter(full_name__in=declared_sanctions)
                new_breach.sanctions_regimes.set(sanctions_regimes)

            new_reference = new_breach.assign_reference()
            new_breach.save()

            # Save Breacher Details to Database
            if not show_check_company_details_page_condition(self):
                breacher_details = cleaned_data["business_or_person_details"]
                self.save_person_or_company_to_db(new_breach, breacher_details, TypeOfRelationshipChoices.breacher)
            else:
                companies_house_details = cleaned_data["do_you_know_the_registered_company_number"]
                self.save_companies_house_company_to_db(new_breach, companies_house_details, TypeOfRelationshipChoices.breacher)

            # Save Supplier Details to Database
            if show_about_the_supplier_page(self):
                supplier_details = cleaned_data["about_the_supplier"]
                self.save_person_or_company_to_db(new_breach, supplier_details, TypeOfRelationshipChoices.supplier)

            # Save Recipient(s) Details to Database
            if end_users := self.request.session.get("end_users", None):
                for end_user in end_users:
                    end_user_details = end_users[end_user]["cleaned_data"]
                    end_user_details["name"] = end_user_details.get("name_of_person", "")
                    self.save_person_or_company_to_db(new_breach, end_user_details, TypeOfRelationshipChoices.recipient)

            # Save Documents to S3 Permanent Bucket
            self.store_documents_in_s3(new_breach.id)
            self.request.session["reference_id"] = new_reference
            self.storage.reset()
            self.storage.current_step = self.steps.first

        return redirect(reverse("report_a_suspected_breach:complete"))


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
            session_keyed_file_name = f"{self.request.session.session_key}/{temporary_file.name}"
            self.file_storage.save(session_keyed_file_name, temporary_file.file)

            # adding the file name to the cache, so we can retrieve it later and confirm they uploaded it
            # we add a unique identifier to the key, so we do not overwrite previous uploads
            redis_cache_key = f"{self.request.session.session_key}{uuid.uuid4()}"
            cache.set(redis_cache_key, temporary_file.name)

            if is_ajax(self.request):
                return JsonResponse(
                    {
                        "success": True,
                        "file_name": temporary_file.name,
                    },
                    status=201,
                )
        if is_ajax(self.request):
            return JsonResponse({"success": True}, status=200)
        else:
            return redirect(get_wizard_step_url("tell_us_about_the_suspected_breach"))

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


class RequestVerifyCodeView(FormView):
    form_class = SummaryForm
    template_name = "report_a_suspected_breach/form_steps/request_verify_code.html"
    success_url = reverse_lazy("report_a_suspected_breach:email_verify")

    def form_valid(self, form: SummaryForm) -> HttpResponse:
        reporter_email_address = self.request.session["reporter_email_address"]
        verify_email(reporter_email_address, self.request)
        return super().form_valid(form)


class EmailVerifyView(FormView):
    form_class = EmailVerifyForm
    template_name = "report_a_suspected_breach/generic_nonwizard_form_step.html"
    success_url = reverse_lazy("report_a_suspected_breach:step", kwargs={"step": "name"})

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
        # we're importing these methods here to avoid circular imports
        from .form_step_conditions import (
            show_name_and_business_you_work_for_page,
            show_name_page,
        )

        if show_name_page(self):
            return reverse_lazy("report_a_suspected_breach:step", kwargs={"step": "name"})
        elif show_name_and_business_you_work_for_page(self):
            return reverse_lazy("report_a_suspected_breach:step", kwargs={"step": "name_and_business_you_work_for"})
        else:
            return reverse_lazy("report_a_suspected_breach:step", kwargs={"step": "start"})


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
        if end_user_uuid := self.request.POST.get("end_user_uuid"):
            end_users = self.request.session.pop("end_users", None)
            end_users.pop(end_user_uuid, None)
            self.request.session["end_users"] = end_users
            self.request.session.modified = True

        return redirect(reverse_lazy("report_a_suspected_breach:step", kwargs={"step": "end_user_added"}))


def is_step_blocked(view: View, request: HttpRequest, current_step: str) -> bool:
    blocked_steps, your_details_in_progress = get_blocked_steps(view)
    if current_step in blocked_steps:
        return True
    if your_details_in_progress:
        steps_to_block_if_email_unverified = ["name", "name_and_business_you_work_for"]
        if current_step in steps_to_block_if_email_unverified:
            if not ReporterEmailVerification.objects.filter(reporter_session=request.session.session_key).latest("date_created"):
                return True
    return False
