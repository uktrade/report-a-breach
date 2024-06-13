from django.urls import reverse
from feedback.models import FeedbackItem
from freezegun import freeze_time


class TestProvideFullFeedbackView:

    @freeze_time("2012-01-14")
    def test_successful(self, rasb_client):
        assert FeedbackItem.objects.count() == 0
        response = rasb_client.post(
            reverse("feedback:collect_full_feedback"),
            data={
                "rating": 1,
                "how_we_could_improve_the_service": "try harder",
                "did_you_experience_any_issues": ["not_found", "lacks_features"],
            },
        )
        assert FeedbackItem.objects.count() == 1
        assert response.status_code == 302
        assert response.url == reverse("feedback:feedback_done")
        feedback_object = FeedbackItem.objects.get()
        assert feedback_object.rating == 1
        assert feedback_object.how_we_could_improve_the_service == "try harder"
        assert feedback_object.did_you_experience_any_issues == ["not_found", "lacks_features"]
        assert feedback_object.created_at.year == 2012
        assert feedback_object.created_at.month == 1
        assert feedback_object.created_at.day == 14

    def test_unsuccessful(self, rasb_client):
        response = rasb_client.post(
            reverse("feedback:collect_full_feedback"),
            data={"rating": 60},
        )
        assert not FeedbackItem.objects.exists()
        assert response.status_code == 200
        assert response.context["form"].is_valid() is False
        assert "rating" in response.context["form"].errors

    def test_amend_feedback(self, rasb_client):
        feedback = FeedbackItem.objects.create(
            rating=2,
            how_we_could_improve_the_service="test",
        )
        rasb_client.post(
            reverse("feedback:amend_feedback", kwargs={"existing_feedback_id": feedback.pk}),
            data={
                "rating": 1,
                "how_we_could_improve_the_service": "try harder",
                "did_you_experience_any_issues": ["not_found", "lacks_features"],
            },
        )
        feedback.refresh_from_db()
        assert feedback.rating == 1
        assert feedback.how_we_could_improve_the_service == "try harder"
