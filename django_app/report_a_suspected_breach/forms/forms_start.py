from datetime import timedelta

from core.forms import BaseForm, BaseModelForm
from core.utils import is_request_ratelimited
from crispy_forms_gds.layout import Field, Fluid, Layout
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.timezone import now
from feedback.crispy_fields import HTMLTemplate
from report_a_suspected_breach.models import Breach, ReporterEmailVerification

Field.template = "core/custom_fields/field.html"


class StartForm(BaseModelForm):
    show_back_button = False

    class Meta:
        model = Breach
        fields = ["reporter_professional_relationship"]
        error_messages = {
            "reporter_professional_relationship": {
                "required": "Select your professional relationship with the business or person suspected of breaching sanctions"
            }
        }
        widgets = {"reporter_professional_relationship": forms.RadioSelect}
        labels = {
            "reporter_professional_relationship": "What is your professional relationship with "
            "the business or person suspected of breaching sanctions?",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["reporter_professional_relationship"].choices.pop(0)


class EmailForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_email_address"]
        help_texts = {
            "reporter_email_address": "We need to send you an email to verify your email address.",
        }
        labels = {
            "reporter_email_address": "What is your email address?",
        }
        error_messages = {
            "reporter_email_address": {
                "required": "Enter your email address",
                "invalid": "Enter an email in the correct format, for example name@example.com",
            },
        }


class EmailVerifyForm(BaseForm):
    bold_labels = False
    form_h1_header = "We've sent you an email"
    revalidate_on_done = False

    email_verification_code = forms.CharField(
        label="Enter the 6 digit security code",
        error_messages={
            "required": "Enter the 6 digit security code we sent to your email",
            "expired": "The code you entered is no longer valid. New code sent",
            "invalid": "Code is incorrect. Enter the 6 digit security code we sent to your email",
            "invalid_after_expired": "The code you entered is no longer valid. Please verify your email again",
        },
        widget=forms.TextInput(attrs={"style": "max-width: 5em"}),
    )

    def clean_email_verification_code(self) -> str:
        # first we check if the request is rate-limited
        if is_request_ratelimited(self.request):
            raise forms.ValidationError("You've tried to verify your email too many times. Try again in 1 minute")

        email_verification_code = self.cleaned_data["email_verification_code"]
        email_verification_code = email_verification_code.replace(" ", "")

        verify_timeout_seconds = settings.EMAIL_VERIFY_TIMEOUT_SECONDS

        verification_object = ReporterEmailVerification.objects.filter(reporter_session=self.request.session.session_key).latest(
            "date_created"
        )

        self.verification_object = verification_object
        verify_code = verification_object.email_verification_code
        if email_verification_code != verify_code:
            raise forms.ValidationError(self.fields["email_verification_code"].error_messages["invalid"], code="invalid")

        # check if the user has submitted the verify code within the specified timeframe
        allowed_lapse = verification_object.date_created + timedelta(seconds=verify_timeout_seconds)
        if allowed_lapse < now():
            time_code_sent = verification_object.date_created

            # 15 minutes ago, show a ‘code has expired’ error message and send the user a new code
            # 2 hours ago, show an ‘incorrect security code’ message, even if the code was correct
            if time_code_sent > (now() - timedelta(hours=2)):
                raise forms.ValidationError(self.fields["email_verification_code"].error_messages["expired"], code="expired")
            else:
                raise forms.ValidationError(
                    self.fields["email_verification_code"].error_messages["invalid_after_expired"], code="invalid_after_expired"
                )

        return email_verification_code

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        if self.request.method == "GET":
            self.is_bound = False

        request_verify_code = reverse_lazy("report_a_suspected_breach:request_verify_code")
        self.helper["email_verification_code"].wrap(
            Field,
            HTMLTemplate(
                html_template_path="report_a_suspected_breach/partials/not_received_code_help_text.html",
                html_context={"request_verify_code": request_verify_code},
            ),
        )


class NameForm(BaseModelForm):
    class Meta:
        model = Breach
        fields = ["reporter_full_name"]
        labels = {
            "reporter_full_name": "What is your full name?",
        }
        error_messages = {
            "reporter_full_name": {"required": "Enter your full name"},
        }


class NameAndBusinessYouWorkForForm(BaseModelForm):
    form_h1_header = "Your details"

    class Meta:
        model = Breach
        fields = ["reporter_full_name", "reporter_name_of_business_you_work_for"]
        labels = {
            "reporter_full_name": "Full name",
            "reporter_name_of_business_you_work_for": "Business you work for",
        }
        help_texts = {
            "reporter_name_of_business_you_work_for": "This is the business that employs you, not the business you're reporting",
        }
        error_messages = {
            "reporter_full_name": {"required": "Enter your full name"},
            "reporter_name_of_business_you_work_for": {"required": "Enter the name of the business you work for"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = None
        self.helper.layout = Layout(
            Field.text("reporter_full_name", field_width=Fluid.ONE_HALF),
            Field.text("reporter_name_of_business_you_work_for", field_width=Fluid.ONE_HALF),
        )
