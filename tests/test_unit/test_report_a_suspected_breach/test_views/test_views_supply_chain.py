from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse, reverse_lazy

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

    def test_deleted_end_user_and_change_success_url(self, rasb_client):
        request = RequestFactory().post("/")
        request.session = rasb_client.session
        request.session["end_users"] = data.end_users
        request.session.save()
        response = rasb_client.post(
            reverse("report_a_suspected_breach:delete_end_user"),
            data={"end_user_uuid": "end_user1", "success_url": "check_your_answers"},
        )
        assert len(rasb_client.session["end_users"]) == 2
        assert response.url == reverse("report_a_suspected_breach:check_your_answers")
        assert response.status_code == 302


class TestZeroEndUsersView:
    def test_add_an_end_user_post(self, rasb_client):
        response = rasb_client.post(
            reverse_lazy("report_a_suspected_breach:zero_end_users"),
            data={
                "do_you_want_to_add_an_end_user": True,
            },
        )
        expected_redirect = HttpResponseRedirect(
            status=302,
            content_type="text/html; charset=utf-8",
            redirect_to=reverse("report_a_suspected_breach:where_were_the_goods_supplied_to") + "?add_another_end_user=yes",
        )
        assert response.status_code == expected_redirect.status_code
        assert response["content-type"] == expected_redirect["content-type"]
        assert response.url == expected_redirect.url

    def test_do_not_add_an_end_user_post(self, rasb_client):
        response = rasb_client.post(
            reverse_lazy("report_a_suspected_breach:zero_end_users"),
            data={
                "do_you_want_to_add_an_end_user": False,
            },
        )
        expected_redirect = HttpResponseRedirect(
            status=302,
            content_type="text/html; charset=utf-8",
            redirect_to=reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain"),
        )
        assert response.status_code == expected_redirect.status_code
        assert response["content-type"] == expected_redirect["content-type"]
        assert response.url == expected_redirect.url

    def test_add_an_end_user_made_available_post(self, rasb_client):
        session = rasb_client.session
        session["made_available_journey"] = True
        session.save()
        response = rasb_client.post(
            reverse_lazy("report_a_suspected_breach:zero_end_users"),
            data={
                "do_you_want_to_add_an_end_user": True,
            },
        )
        expected_redirect = HttpResponseRedirect(
            status=302,
            content_type="text/html; charset=utf-8",
            redirect_to=reverse("report_a_suspected_breach:where_were_the_goods_made_available_to") + "?add_another_end_user=yes",
        )
        assert response.status_code == expected_redirect.status_code
        assert response["content-type"] == expected_redirect["content-type"]
        assert response.url == expected_redirect.url

    def test_do_not_add_an_end_user_made_available_post(self, rasb_client):
        session = rasb_client.session
        session["made_available_journey"] = True
        session.save()
        response = rasb_client.post(
            reverse_lazy("report_a_suspected_breach:zero_end_users"),
            data={
                "do_you_want_to_add_an_end_user": False,
            },
        )
        expected_redirect = HttpResponseRedirect(
            status=302,
            content_type="text/html; charset=utf-8",
            redirect_to=reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain"),
        )
        assert response.status_code == expected_redirect.status_code
        assert response["content-type"] == expected_redirect["content-type"]
        assert response.url == expected_redirect.url
