from django.urls import reverse


class TestWhereWereTheGoodsMadeAvailableFromView:
    def test_success(self, rasb_client):
        session = rasb_client.session
        session["company_details"] = {
            "do_you_know_the_registered_company_number": "yes",
            "registered_office_address": "123 Fake Street, London, E1 4UD",
        }
        session.save()

        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_made_available_from"),
            data={"where_were_the_goods_made_available_from": "different_uk_address"},
        )

        assert response.url == reverse("report_a_suspected_breach:about_the_supplier", kwargs={"is_uk_address": True})

        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_made_available_from"),
            data={"where_were_the_goods_made_available_from": "i_do_not_know"},
        )

        assert response.url == reverse("report_a_suspected_breach:where_were_the_goods_made_available_to")

        assert rasb_client.session.get("made_available_journey", False)

    def test_redirect_after_post(self, rasb_client):
        session = rasb_client.session
        session["company_details"] = {
            "do_you_know_the_registered_company_number": "yes",
            "registered_office_address": "123 Fake Street, London, E1 4UD",
        }
        session.save()

        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_made_available_from")
            + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
            data={"where_were_the_goods_made_available_from": "i_do_not_know"},
        )
        assert response.url == reverse("report_a_suspected_breach:check_your_answers")

        response = rasb_client.post(
            reverse("report_a_suspected_breach:where_were_the_goods_made_available_from")
            + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
            data={"where_were_the_goods_made_available_from": "different_uk_address"},
        )
        assert not response.url == reverse("report_a_suspected_breach:check_your_answers")

    def test_get_form_kwargs(self, rasb_client):
        session = rasb_client.session
        session["company_details"] = {
            "do_you_know_the_registered_company_number": "yes",
            "registered_office_address": "123 Fake Street, London, E1 4UD",
        }
        session.save()

        response = rasb_client.get(
            reverse("report_a_suspected_breach:where_were_the_goods_made_available_from")
            + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
        )
        form = response.context["form"]
        assert form.fields["where_were_the_goods_made_available_from"].choices[0].label == "123 Fake Street, London, E1 4UD"

        session["company_details"] = {}
        session["business_or_person_details"] = {
            "address_line_1": "123 Fake Street",
            "address_line_2": "test",
            "postal_code": "E1 4UD",
            "country": "England",
        }
        session.save()

        response = rasb_client.get(
            reverse("report_a_suspected_breach:where_were_the_goods_made_available_from")
            + "?redirect_to_url=report_a_suspected_breach:check_your_answers",
        )
        form = response.context["form"]
        assert (
            form.fields["where_were_the_goods_made_available_from"].choices[0].label
            == "123 Fake Street,\n test,\n E1 4UD,\n United Kingdom"
        )
