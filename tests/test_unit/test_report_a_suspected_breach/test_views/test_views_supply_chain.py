from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse, reverse_lazy

# from report_a_suspected_breach.forms.forms_supply_chain import EndUserAddedForm
from report_a_suspected_breach.views.views_supply_chain import (
    AboutTheSupplierView,
    WhereWereTheGoodsMadeAvailableToView,
)

from django_app.report_a_suspected_breach.views.views_supply_chain import (  # EndUserAddedView,
    AboutTheEndUserView,
)

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


class TestAboutTheEndUserView:
    def test_get_form_kwargs_no_end_users(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["end_users_location"] = {"end_user_1": {"is_uk_address": "True"}}
        request_object.session["is_uk_address"] = True
        request_object.session.save()
        view = AboutTheEndUserView()
        # UK Address
        view.setup(request_object, in_the_uk=True)
        response = view.get_form_kwargs()
        assert response["form_h1_header"] == "End-user 1 details"
        assert response["data"] is None

    def test_get_form_kwargs_uk_address(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["end_users"] = data.end_users
        request_object.session["end_users_location"] = {"end_user_1": {"is_uk_address": "True"}}
        request_object.session["is_uk_address"] = True
        request_object.session.save()
        view = AboutTheEndUserView()
        # UK Address
        view.setup(request_object, in_the_uk=True, end_user_uuid="end_user2")
        response = view.get_form_kwargs()
        assert response["form_h1_header"] == "End-user 2 details"
        assert response["data"]["country"] == "GB"

    def test_get_form_kwargs_non_uk_address(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["end_users"] = data.end_users
        request_object.session["end_users_location"] = {"end_user_2": {"is_uk_address": False}}
        request_object.session["is_uk_address"] = False
        request_object.session.save()
        request_object.GET = {"end_user_uuid": "end_user3"}
        view = AboutTheEndUserView()
        view.setup(request_object, in_the_uk=False, end_user_uuid="end_user3")
        response = view.get_form_kwargs()
        assert response["form_h1_header"] == "End-user 3 details"
        assert response["data"]["country"] == "NZ"

    def test_get_form_kwargs_add_another_end_user(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["end_users"] = data.end_users
        request_object.session["end_users_location"] = {"end_user_1": {"is_uk_address": True}}
        request_object.session["is_uk_address"] = True
        request_object.session.save()
        view = AboutTheEndUserView()
        view.setup(request_object, in_the_uk=True, end_user_uuid="end_user4")
        response = view.get_form_kwargs()
        assert response["form_h1_header"] == "End-user 4 details"
        assert response["data"] is None

    # def test_form_valid(self, request_object, rasb_client):
    #     request_object.session = rasb_client.session
    #     request_object.session["end_users"] = {}
    #     request_object.save()
    #     view = AboutTheEndUserView()


class TestWhereWereTheGoodsMadeAvailableToView:
    def test_redirect_after_post(self, rasb_client):
        session = rasb_client.session
        session["company_details"] = {
            "do_you_know_the_registered_company_number": "yes",
            "registered_office_address": "123 Fake Street, London, E1 4UD",
        }
        session.save()

        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_from")
            + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
            data={"where_were_the_goods_supplied_from": "i_do_not_know"},
        )

        assert response.url == reverse("report_a_suspected_breach:check_your_answers")

        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_from")
            + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
            data={"where_were_the_goods_supplied_from": "different_uk_address"},
        )
        assert not response.url == reverse("report_a_suspected_breach:check_your_answers")

    def test_get_form_kwargs_with_and_without_end_user(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session.save()
        view = WhereWereTheGoodsMadeAvailableToView()
        view.setup(request_object)
        response = view.get_form_kwargs()
        assert "data" not in response
        assert "end_user_uuid" not in response

        request_object.session["end_users_location"] = {"end_user_uuid": {"dirty_data": {"field1": "value1"}}}
        request_object.session.save()
        view.setup(request_object, end_user_uuid="end_user_uuid")
        response = view.get_form_kwargs()
        assert "data" in response
        assert response["data"] == {"field1": "value1"}
        assert response["end_user_uuid"] == "end_user_uuid"

    def test_get_form_kwargs_no_end_user_data(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["end_users_location"] = {"end_user_uuid": "123456"}
        request_object.session.save()
        view = WhereWereTheGoodsMadeAvailableToView()
        view.setup(request_object, end_user_uuid="123456")
        response = view.get_form_kwargs()
        assert "data" not in response
        assert response["end_user_uuid"] == "123456"

    def test_get_form_kwargs_no_get_method(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session.save()
        request_object.method = "POST"
        request_object.FILES = {}
        request_object.POST = {}

        view = WhereWereTheGoodsMadeAvailableToView()
        view.setup(request_object, end_user_uuid="123456")
        response = view.get_form_kwargs()
        assert response["data"] == {}
        assert "end_user_uuid" not in response


class TestAboutTheSupplierView:
    def test_get_form_kwargs_uk_address(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session.save()
        view = AboutTheSupplierView()
        view.setup(request_object, is_uk_address="True")
        response = view.get_form_kwargs()
        assert response["is_uk_address"] is True

    def test_get_form_kwargs_non_uk_address(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session.save()
        view = AboutTheSupplierView()
        view.setup(request_object, is_uk_address=False)
        response = view.get_form_kwargs()
        assert response["is_uk_address"] is False

    def test_get_success_url(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session.save()

        view = AboutTheSupplierView()
        view.request = request_object

        success_url = view.get_success_url()
        assert success_url == reverse("report_a_suspected_breach:where_were_the_goods_supplied_to")

        request_object.session["made_available_journey"] = True
        request_object.session.save()
        success_url = view.get_success_url()
        assert success_url == reverse("report_a_suspected_breach:where_were_the_goods_made_available_to")


# class TestEndUserAddedView:
#     # def test_get_context_data(self, request_object, mock_get_all):
#
#     def test_get_success_url(self, request_object, rasb_client):
#         request_object.session = rasb_client.session
#         request_object.session.save()
#         view = EndUserAddedView()
#         view.request =
