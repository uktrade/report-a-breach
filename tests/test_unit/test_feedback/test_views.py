from django.urls import reverse
from feedback.models import FeedbackItem


class TestProvidePartialFeedbackView:
    feedback_post_dict = {
        "rating": 1,
        "what_did_not_work_so_well": ["process_not_clear"],
        "how_we_could_improve_the_service": "try harder",
    }

    def test_successful(self, rasb_client):
        assert FeedbackItem.objects.count() == 0
        response = rasb_client.post(reverse("feedback:collect_feedback"), data=self.feedback_post_dict)
        assert FeedbackItem.objects.count() == 1
        new_feedback = FeedbackItem.objects.first()

        assert response.status_code == 302
        assert response.url == reverse("feedback:amend_feedback", kwargs={"existing_feedback_id": new_feedback.pk})

    def test_ajax_successful(self, rasb_client):
        assert FeedbackItem.objects.count() == 0
        response = rasb_client.post(
            reverse("feedback:collect_feedback"),
            data=self.feedback_post_dict,
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 200
        assert FeedbackItem.objects.count() == 1
        new_feedback = FeedbackItem.objects.first()

        assert response.json() == {
            "feedback_id": str(new_feedback.pk),
            "second_step_url": reverse("feedback:amend_feedback", kwargs={"existing_feedback_id": new_feedback.pk}),
            "success": True,
        }

    def test_amend_feedback(self, rasb_client):
        feedback = FeedbackItem.objects.create(
            rating=2,
            what_did_not_work_so_well=["process_not_clear"],
            how_we_could_improve_the_service="test",
        )
        rasb_client.post(
            reverse("feedback:collect_feedback"),
            data=self.feedback_post_dict | {"existing_feedback_id": feedback.pk},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        feedback.refresh_from_db()
        assert feedback.rating == self.feedback_post_dict["rating"]
        assert feedback.what_did_not_work_so_well == self.feedback_post_dict["what_did_not_work_so_well"]
        assert feedback.how_we_could_improve_the_service == self.feedback_post_dict["how_we_could_improve_the_service"]

    def test_unsuccessful_ajax(self, rasb_client):
        response = rasb_client.post(
            reverse("feedback:collect_feedback"),
            data={"rating": 60},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert response.status_code == 400
        assert response.json() == {
            "errors": {"rating": ["Select a valid choice. 60 is not one of the available choices."]},
            "success": False,
        }
        assert not FeedbackItem.objects.exists()


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
