import os

from core.document_storage import TemporaryDocumentStorage
from core.forms import BaseForm, BaseModelForm
from core.utils import get_mime_type
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Field, Layout
from django import forms
from django.utils.html import escape
from django_chunk_upload_handlers.clam_av import VirusFoundInFileException
from report_a_suspected_breach.fields import MultipleFileField
from report_a_suspected_breach.models import Breach, UploadedDocument
from utils.s3 import get_all_session_files

Field.template = "core/custom_fields/field.html"


class UploadDocumentsForm(BaseForm):
    revalidate_on_done = False
    document = MultipleFileField(
        label="Upload a file",
        help_text="Maximum individual file size 100MB. Maximum number of uploads 10",
        required=False,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["document"].widget.attrs["class"] = "govuk-file-upload moj-multi-file-upload__input"
        self.fields["document"].widget.attrs["name"] = "document"
        # redefining this to remove the 'Continue' button from the helper
        self.helper = FormHelper()
        self.helper.layout = Layout("document")

    def clean_document(self) -> list[UploadedDocument]:
        documents = self.cleaned_data.get("document")
        for document in documents:

            # does the document contain a virus?
            try:
                document.readline()
            except VirusFoundInFileException:
                documents.remove(document)
                raise forms.ValidationError(
                    "A virus was found in one of the files you uploaded.",
                )

            # is the document a valid file type?
            mimetype = get_mime_type(document.file)
            valid_mimetype = mimetype in [
                # word documents
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
                # spreadsheets
                "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                # powerpoints
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                # pdf
                "application/pdf",
                # other
                "text/plain",
                "text/csv",
                "application/zip",
                "text/html",
                # images
                "image/jpeg",
                "image/png",
            ]

            _, file_extension = os.path.splitext(document.name)
            valid_extension = file_extension in [
                # word documents
                ".doc",
                ".docx",
                ".odt",
                ".fodt",
                # spreadsheets
                ".xls",
                ".xlsx",
                ".ods",
                ".fods",
                # powerpoints
                ".ppt",
                ".pptx",
                ".odp",
                ".fodp",
                # pdf
                ".pdf",
                # other
                ".txt",
                ".csv",
                ".zip",
                ".html",
                # images
                ".jpeg",
                ".jpg",
                ".png",
            ]

            if not valid_mimetype or not valid_extension:
                raise forms.ValidationError(
                    f"{escape(document.name)} cannot be uploaded, it is not a valid file type", code="invalid_file_type"
                )

            # has the user already uploaded 10 files?
            if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
                if len(session_files) + 1 > 10:
                    raise forms.ValidationError("You can only select up to 10 files at the same time", code="too_many")

            # is the document too large?
            if document.size > 104857600:
                raise forms.ValidationError(f"{document.name} must be smaller than 100 MB", code="too_large")

        return documents


class TellUsAboutTheSuspectedBreachForm(BaseModelForm):
    class Meta:
        model = Breach
        # todo - make all fields variables a tuple
        fields = ["tell_us_about_the_suspected_breach"]
        labels = {
            "tell_us_about_the_suspected_breach": "Give a summary of the breach",
        }
        help_texts = {
            "tell_us_about_the_suspected_breach": "You can also include anything you've not already told us or "
            "uploaded. You could add specific details, such as any "
            "licence numbers or shipping numbers.",
        }
        error_messages = {
            "tell_us_about_the_suspected_breach": {"required": "Enter a summary of the breach"},
        }
