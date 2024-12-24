import datetime

from django.urls import reverse

from tests.factories import FeedbackFactory


class TestViewAllFeedbackView:
    def test_get_queryset(self, vasb_client_logged_in):
        FeedbackFactory.create_batch(3)
        response = vasb_client_logged_in.get(reverse("view_a_suspected_breach:view_all_feedback"))
        objects = response.context["object_list"]
        assert objects.count() == 3

    def test_get_queryset_with_get_parameters(self, vasb_client_logged_in):
        feedback_items = FeedbackFactory.create_batch(3)
        feedback_items[0].created_at = datetime.datetime.now()
        feedback_items[1].created_at = datetime.datetime.now() - datetime.timedelta(days=5)
        feedback_items[2].created_at = datetime.datetime.now() - datetime.timedelta(days=10)
        feedback_items[0].save()
        feedback_items[1].save()
        feedback_items[2].save()

        # date_max query parameter
        query_params = {"date_max": datetime.datetime.now().date() - datetime.timedelta(days=1)}

        response = vasb_client_logged_in.get(reverse("view_a_suspected_breach:view_all_feedback"), data=query_params)
        objects = response.context["object_list"]
        assert objects.count() == 2
        object_ids = list(objects.values_list("id", flat=True))
        assert feedback_items[0].id not in object_ids
        assert feedback_items[1].id in object_ids
        assert feedback_items[2].id in object_ids

        # date_min query parameter
        query_params = {"date_min": datetime.datetime.now().date() - datetime.timedelta(days=5)}

        response = vasb_client_logged_in.get(reverse("view_a_suspected_breach:view_all_feedback"), data=query_params)
        objects = response.context["object_list"]
        assert objects.count() == 2
        object_ids = list(objects.values_list("id", flat=True))
        assert feedback_items[0].id in object_ids
        assert feedback_items[1].id in object_ids
        assert feedback_items[2].id not in object_ids

        # date_max and date_min query parameters

        query_params = {
            "date_max": datetime.datetime.now().date() - datetime.timedelta(days=1),
            "date_min": datetime.datetime.now().date() - datetime.timedelta(days=6),
        }

        response = vasb_client_logged_in.get(reverse("view_a_suspected_breach:view_all_feedback"), data=query_params)
        objects = response.context["object_list"]
        assert objects.count() == 1
        object_ids = list(objects.values_list("id", flat=True))
        assert feedback_items[0].id not in object_ids
        assert feedback_items[1].id in object_ids
        assert feedback_items[2].id not in object_ids

    def test_get_did_you_experience_any_issues_display(self, request_object):
        feedback_items = FeedbackFactory.create_batch(3)
        feedback_items[0].did_you_experience_any_issues = ["difficult"]
        feedback_items[0].save()
        feedback_items[1].did_you_experience_any_issues = ["not_found", "lacks_features"]
        feedback_items[1].save()
        feedback_items[2].did_you_experience_any_issues = []
        feedback_items[2].save()
        assert feedback_items[0].get_did_you_experience_any_issues_display() == "I found it difficult to navigate"
        assert (
            feedback_items[1].get_did_you_experience_any_issues_display()
            == "I did not find what I was looking for,\nThe system lacks the feature I need"
        )
        assert feedback_items[2].get_did_you_experience_any_issues_display() == ""
