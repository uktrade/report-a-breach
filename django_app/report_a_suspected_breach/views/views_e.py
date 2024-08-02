import logging
import uuid
from typing import Any

from core.base_views import BaseFormView
from core.document_storage import TemporaryDocumentStorage
from core.utils import is_ajax
from django.core.cache import cache
from django.forms import Form
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from report_a_suspected_breach.forms import forms_e as forms
from utils.s3 import (
    generate_presigned_url,
    get_all_session_files,
    get_user_uploaded_files,
)

logger = logging.getLogger(__name__)


class UploadDocumentsView(BaseFormView):
    """View for uploading documents. This view is used in the wizard flow, but can also be accessed directly.

    Accepts both Ajax and non-Ajax requests, to accommodate both JS and non-JS users respectively."""

    form_class = forms.UploadDocumentsForm
    template_name = "report_a_suspected_breach/form_steps/upload_documents.html"
    file_storage = TemporaryDocumentStorage()
    success_url = reverse_lazy("report_a_suspected_breach:tell_us_about_the_suspected_breach")

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
            return super().form_valid(form)

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


class TellUsAboutTheSuspectedBreachView(BaseFormView):
    form_class = forms.TellUsAboutTheSuspectedBreachForm
    success_url = reverse_lazy("report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "summary"})
