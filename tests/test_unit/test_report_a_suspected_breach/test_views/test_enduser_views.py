from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestDeleteEndUserView:
    def test_successful_post(self, rasb_client):
        request = RequestFactory().post("/")
        request.session = rasb_client.session
        request.session["end_users"] = data.end_users
        end_user_id = "end_user1"
        request.session.save()
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_end_user"),
            data={"end_user_uuid": end_user_id},
        )
        assert "end_user1" not in rasb_client.session["end_users"].keys()
        assert rasb_client.session["end_users"] != data.end_users
        assert response.url == reverse("report_a_suspected_breach:end_user_added")
        assert response.status_code == 302

    def test_delete_all_end_users_post(self, rasb_client):
        request = RequestFactory().post("/")
        request.session = rasb_client.session
        request.session["end_users"] = data.end_users
        request.session.save()
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_end_user"),
            data={"end_user_uuid": "end_user1"},
        )
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_end_user"),
            data={"end_user_uuid": "end_user2"},
        )
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_end_user"),
            data={"end_user_uuid": "end_user3"},
        )

        assert rasb_client.session["end_users"] == {}
        assert response.url == reverse("report_a_suspected_breach:zero_end_users")
        assert response.status_code == 302

    def test_unsuccessful_post(self, rasb_client):
        request_object = RequestFactory().get("/")
        request_object.session = rasb_client.session
        request_object.session["end_users"] = data.end_users
        request_object.session.save()
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_end_user"),
        )
        assert rasb_client.session["end_users"] == data.end_users
        assert response.url == reverse("report_a_suspected_breach:end_user_added")
        assert response.status_code == 302
