from unittest.mock import patch

from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.test import RequestFactory
from report_a_suspected_breach.models import ReporterEmailVerification
from report_a_suspected_breach.views.views_end import (
    CheckYourAnswersView,
    CompleteView,
    DeclarationView,
)

from django_app.report_a_suspected_breach.forms.forms_end import DeclarationForm

from . import data


class TestCheckYourAnswersView:
    @patch("report_a_suspected_breach.views.views_end.get_all_cleaned_data")
    def test_get_context_data(self, mocked_get_all_cleaned_data, request_object):
        mocked_get_all_cleaned_data.return_value = data.cleaned_data
        view = CheckYourAnswersView()
        view.setup(request_object)
        context_data = view.get_context_data()
        assert context_data["form_data"] == data.cleaned_data
        assert not context_data["is_third_party_relationship"]


class TestDeclarationView:
    @patch("report_a_suspected_breach.models.get_all_cleaned_data")
    def test_form_valid(self, mocked_get_all_cleaned_data, request_object, rasb_client):
        mocked_get_all_cleaned_data.return_value = data.cleaned_data
        request_object.session = rasb_client.session
        request_session = Session.objects.get(session_key=request_object.session.session_key)
        reporter_object = ReporterEmailVerification.objects.create(
            reporter_session=request_session, email_verification_code="012345", verified=True
        )
        reporter_object.save()
        view = DeclarationView()
        view.setup(request_object)
        response = view.form_valid(DeclarationForm(data={}))
        assert response.status_code == 302
        assert response.url == "/report/submission-complete"


class TestCompleteView:

    def test_get_context_data(self, breach_object, rasb_client):
        request_object = RequestFactory().get("/")
        breach_object.save()
        request_object.session = rasb_client.session
        request_object.session["breach_id"] = breach_object.id

        session = rasb_client.session
        breach_object.reporter_session = Session.objects.get(session_key=session.session_key)
        breach_object.save()
        session["breach_id"] = breach_object.id

        view = CompleteView()
        view.setup(request_object)

        response = view.get(request_object)

        # Assert returns success redirect
        expected_response = HttpResponse(status=200, content_type="text/html; charset=utf-8")
        breach = response.context_data["breach"]
        assert breach.id == breach_object.id
        assert response.status_code == expected_response.status_code
        assert response["content-type"] == expected_response["content-type"]
