from django.http import HttpResponse
from django.test import RequestFactory
from feedback.forms import FeedbackForm
from report_a_suspected_breach.views import CompleteView


class TestCompleteView:

    def test_get_context_data(self, breach_object, rasb_client):
        request_object = RequestFactory().get("/")

        request_object.session = rasb_client.session
        session = rasb_client.session
        session.save()
        view = CompleteView()
        view.setup(request_object)

        response = view.get(request_object)

        # Assert returns success redirect
        expected_response = HttpResponse(status=200, content_type="text/html; charset=utf-8")
        feedback_form = response.context_data["feedback_form"]
        assert isinstance(feedback_form, FeedbackForm)
        breach = response.context_data["breach"]
        assert breach.id == breach_object.id
        assert response.status_code == expected_response.status_code
        assert response["content-type"] == expected_response["content-type"]
