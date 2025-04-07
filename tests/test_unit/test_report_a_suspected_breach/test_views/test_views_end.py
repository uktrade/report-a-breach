import uuid
from unittest.mock import patch

from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
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

    @patch("report_a_suspected_breach.views.views_end.get_all_session_files")
    def test_session_files_are_uploaded(self, mock_get_files, rasb_client):
        mock_get_files.return_value = {"key1": {"file_name": "test.png"}}
        response = rasb_client.get(reverse("report_a_suspected_breach:check_your_answers"))
        assert response.status_code == 200
        assert mock_get_files.called

        assert "form_data" in response.context
        assert "session_files" in response.context["form_data"]
        assert response.context["form_data"]["session_files"] == {"key1": {"file_name": "test.png"}}

    @patch("report_a_suspected_breach.views.views_end.get_all_cleaned_data")
    def test_end_users_in_session(self, mocked_get_all_cleaned_data, request_object, rasb_client):
        mocked_get_all_cleaned_data.return_value = data.cleaned_data
        request_object.session = rasb_client.session
        request_object.session["end_users"] = ["User 1", "User 2"]
        request_object.session.save()

        view = CheckYourAnswersView()
        view.setup(request_object)
        context_data = view.get_context_data()

        assert "end_users" in context_data["form_data"]
        assert context_data["form_data"]["end_users"] == ["User 1", "User 2"]

    @patch("report_a_suspected_breach.views.views_end.get_cleaned_data_for_step")
    def test_same_address_is_true(self, mocked_get_cleaned_data_for_step, request_object, rasb_client):
        return None

    @patch("report_a_suspected_breach.views.views_end.get_cleaned_data_for_step")
    def test_same_address_is_false(self, mocked_get_cleaned_data_for_step, request_object):
        return None


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

    def test_no_breach_id_redirect(self, rasb_client, breach_object):
        session = rasb_client.session
        session["breach_id"] = str(uuid.uuid4())
        session.save()

        response = rasb_client.get(reverse("report_a_suspected_breach:complete"))
        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:initial_redirect_view")
