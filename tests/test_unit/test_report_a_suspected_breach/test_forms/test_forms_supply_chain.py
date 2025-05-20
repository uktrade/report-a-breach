from report_a_suspected_breach.forms.forms_supply_chain import (
    AboutTheEndUserForm,
    WhereWereTheGoodsSuppliedFromForm,
    ZeroEndUsersForm,
)


class TestAboutTheEndUserForm:
    def test_postal_code_validation(self):
        form = AboutTheEndUserForm(data={"postal_code": "SW1A 1AA"}, is_uk_address=True)
        assert form.is_valid()

        form = AboutTheEndUserForm(data={"postal_code": "123"}, is_uk_address=True)
        assert not form.is_valid()
        assert "postal_code" in form.errors
        assert form.errors.as_data()["postal_code"][0].code == "invalid"

    def test_valid_website_url(self):
        form = AboutTheEndUserForm(data={"website": "example.com"})
        form.is_valid()
        assert form.cleaned_data["website"] == "http://example.com"

        form = AboutTheEndUserForm(data={"website": "http://example.com"})
        form.is_valid()
        assert form.cleaned_data["website"] == "http://example.com"

        form = AboutTheEndUserForm(data={"website": "https://example.com"})
        form.is_valid()
        assert form.cleaned_data["website"] == "https://example.com"

    def test_invalid_website_url(self):
        form = AboutTheEndUserForm(data={"website": "https123://example.com"})
        assert not form.is_valid()
        assert form.errors["website"][0] == "Enter website in the correct format, such as www.example.com or example.com"

        form = AboutTheEndUserForm(data={"website": "example"})
        assert not form.is_valid()
        assert form.errors["website"][0] == "Enter website in the correct format, such as www.example.com or example.com"


class TestZeroEndUsersForm:
    def test_do_you_want_to_add_an_end_user_validation(self):
        form = ZeroEndUsersForm(data={"do_you_want_to_add_an_end_user": True})
        assert form.is_valid()
        form = ZeroEndUsersForm(data={})
        assert not form.is_valid()
        assert "do_you_want_to_add_an_end_user" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_an_end_user"][0].code == "required"


class TestWhereWereTheGoodsSuppliedFromForm:
    def test_init_address_string(self):
        form = WhereWereTheGoodsSuppliedFromForm(address_string="")
        choices = form.fields["where_were_the_goods_supplied_from"].choices
        assert "same_address" not in choices[0]

        # with address
        form2 = WhereWereTheGoodsSuppliedFromForm(address_string="1 Test Street")
        choices = form2.fields["where_were_the_goods_supplied_from"].choices
        assert "same_address" in [choice[0] for choice in choices]
