from django.urls import reverse
from feedback.models import FeedbackItem


class TestProvideFullFeedbackView:
    def test_successful(self, rasb_client):
        assert FeedbackItem.objects.count() == 0
        response = rasb_client.post(
            reverse("feedback:collect_full_feedback"),
            data={
                "rating": 1,
                "what_did_not_work_so_well": ["process_not_clear"],
                "how_we_could_improve_the_service": "try harder",
            },
        )
        assert FeedbackItem.objects.count() == 1
        assert response.status_code == 302
        assert response.url == reverse("feedback:feedback_done")

    def test_unsuccessful(self, rasb_client):
        response = rasb_client.post(
            reverse("feedback:collect_full_feedback"),
            data={"rating": 60},
        )
        assert not FeedbackItem.objects.exists()
        assert response.status_code == 302
        assert response.url == reverse("feedback:feedback_done")

    def test_amend_feedback(self, rasb_client):
        feedback = FeedbackItem.objects.create(
            rating=2,
            what_did_not_work_so_well=["process_not_clear"],
            how_we_could_improve_the_service="test",
        )
        rasb_client.post(
            reverse("feedback:amend_feedback", kwargs={"existing_feedback_id": feedback.pk}),
            data={
                "rating": 1,
                "what_did_not_work_so_well": ["process_not_clear"],
                "how_we_could_improve_the_service": "try harder",
            },
        )
        feedback.refresh_from_db()
        assert feedback.rating == 1
        assert feedback.what_did_not_work_so_well == ["process_not_clear"]
        assert feedback.how_we_could_improve_the_service == "try harder"
