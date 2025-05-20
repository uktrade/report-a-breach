from django.http import HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse, reverse_lazy
from report_a_suspected_breach.views.views_supply_chain import (
    AboutTheSupplierView,
    WhereWereTheGoodsMadeAvailableToView,
    WhereWereTheGoodsSuppliedFromView,
)

from django_app.report_a_suspected_breach.views.views_supply_chain import (
    AboutTheEndUserView,
    EndUserAddedView,
    forms,
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

    def test_form_valid(self, request_object, rasb_client):
        view = AboutTheEndUserView()

        request_object.session = rasb_client.session
        view.request = request_object
        view.kwargs = {}

        end_user_uuid = "123456"
        view.kwargs["end_user_uuid"] = end_user_uuid

        test_form_data = {
            "name": "John Smith",
            "address_line_1": "1 Test Road",
        }

        form = forms.AboutTheEndUserForm(data=test_form_data)
        form.is_valid()
        view.form_valid(form)

        assert end_user_uuid in request_object.session["end_users"]
        assert request_object.session["end_users"][end_user_uuid]["cleaned_data"] == form.cleaned_data
        assert request_object.session["end_users"][end_user_uuid]["dirty_data"] == form.data


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

    def test_form_valid(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["end_users_location"] = {"end_user_uuid": "123456"}
        request_object.session.save()

        view = WhereWereTheGoodsMadeAvailableToView()
        view.setup(request_object)

        view.kwargs = {"end_user_uuid": "123456"}

        form = forms.AboutTheEndUserForm(data={"where_were_the_goods_made_available_to": "in_the_uk"})
        form.is_valid()
        view.form_valid(form)

        assert "123456" in request_object.session["end_users_location"]
        assert request_object.session["end_users_location"]["123456"]["cleaned_data"] == form.cleaned_data

        # without end_user_uuid
        request_object.session = rasb_client.session
        request_object.session["end_users_location"] = {}
        request_object.session.save()

        view = WhereWereTheGoodsMadeAvailableToView()
        view.setup(request_object)

        view.kwargs = {}

        form = forms.AboutTheEndUserForm(data={"where_were_the_goods_made_available_to": "in_the_uk"})
        form.is_valid()
        view.form_valid(form)

        assert request_object.session["end_users_location"] == {}


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


class TestWhereWereTheGoodsSuppliedFromView:
    def test_get_form_kwargs_uk_address(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["company_details"] = {
            "do_you_know_the_registered_company_number": "yes",
            "readable_address": "1 Test Road, London, UK",
        }
        request_object.session.save()
        view = WhereWereTheGoodsSuppliedFromView()
        view.setup(request_object)
        kwargs = view.get_form_kwargs()
        assert kwargs["address_string"] == "1 Test Road, London, UK"

    def test_get_success_url(self, request_object, rasb_client):
        # if the choice is same_address
        session = rasb_client.session
        session["company_details"] = {
            "do_you_know_the_registered_company_number": "yes",
            "registered_office_address": "123 Fake Street, London, E1 4UD",
        }
        session.save()
        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_from"),
            data={"where_were_the_goods_supplied_from": "same_address"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:where_were_the_goods_supplied_to")

        # if the choice is the uk but a different uk address
        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_from"),
            data={"where_were_the_goods_supplied_from": "different_uk_address"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:about_the_supplier", kwargs={"is_uk_address": "True"})

        # if the choice is outside_the_uk
        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_from"),
            data={"where_were_the_goods_supplied_from": "outside_the_uk"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:about_the_supplier", kwargs={"is_uk_address": "False"})

        # if the choice is i_do_not_know
        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_from"),
            data={"where_were_the_goods_supplied_from": "i_do_not_know"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:where_were_the_goods_supplied_to")

        # if the choice is they_have_not_been_supplied
        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_from"),
            data={"where_were_the_goods_supplied_from": "they_have_not_been_supplied"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:where_were_the_goods_made_available_from")


class TestWhereWereTheGoodsSuppliedToView:
    def test_get_success_url(self, request_object, rasb_client):
        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_to"),
            data={"where_were_the_goods_supplied_to": "i_do_not_know"},
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")

        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_supplied_to"),
            data={"where_were_the_goods_supplied_to": "in_the_uk"},
        )

        assert response.status_code == 302
        assert rasb_client.session["is_uk_address"] is True


class TestEndUserAddedView:
    def test_get_context_data(self, request_object, rasb_client):
        request_object.session = rasb_client.session
        request_object.session["end_users"] = {"end_user1": {"name": "test end user"}}
        request_object.session["made_available_journey"] = True
        request_object.session.save()

        view = EndUserAddedView()
        view.setup(request_object)
        context = view.get_context_data()
        assert "end_users" in context
        assert "end_user1" in context["end_users"]
        assert "is_made_available_journey" in context
        assert context["is_made_available_journey"] is True

    def test_get_success_url(self, request_object, rasb_client):
        # if the user wants to add another end user and made_available_journey = false
        response = rasb_client.post(
            reverse("report_a_suspected_breach:end_user_added"), data={"do_you_want_to_add_another_end_user": True}
        )

        assert response.status_code == 302
        expected_url = f"{reverse('report_a_suspected_breach:where_were_the_goods_supplied_to')}?add_another_end_user=yes"
        assert response.url == expected_url

        # if the user wants to add another end user and made_available_journey = true
        session = rasb_client.session
        session["made_available_journey"] = True
        session.save()
        response = rasb_client.post(
            reverse("report_a_suspected_breach:end_user_added"), data={"do_you_want_to_add_another_end_user": True}
        )

        assert response.status_code == 302
        expected_url = f"{reverse('report_a_suspected_breach:where_were_the_goods_made_available_to')}?add_another_end_user=yes"
        assert response.url == expected_url

        # if the user doesn't want to add another end user
        response = rasb_client.post(
            reverse("report_a_suspected_breach:end_user_added"), data={"do_you_want_to_add_another_end_user": False}
        )

        assert response.status_code == 302
        assert response.url == reverse("report_a_suspected_breach:were_there_other_addresses_in_the_supply_chain")
