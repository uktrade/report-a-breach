from core import forms


class TestCookiesConsentForm:
    def test_consent_choice_required(self):
        form = forms.CookiesConsentForm(data={"do_you_want_to_accept_analytics_cookies": None})
        assert not form.is_valid()
        assert "do_you_want_to_accept_analytics_cookies" in form.errors

        form = forms.CookiesConsentForm(data={"do_you_want_to_accept_analytics_cookies": ""})
        assert not form.is_valid()
        assert "do_you_want_to_accept_analytics_cookies" in form.errors

    def test_consent_to_cookies_valid(self):
        form = forms.CookiesConsentForm(data={"do_you_want_to_accept_analytics_cookies": "True"})
        assert form.is_valid()
        assert "do_you_want_to_accept_analytics_cookies" not in form.errors

    def test_non_consent_cookies_valid(self):
        form = forms.CookiesConsentForm(data={"do_you_want_to_accept_analytics_cookies": "False"})
        assert form.is_valid()
        assert "do_you_want_to_accept_analytics_cookies" not in form.errors


class TestHideCookiesForm:
    def test_hide_cookies_any_submit_valid(self):
        form = forms.HideCookiesForm(data={"hide_cookies": "True"})
        assert form.is_valid()
        assert "hide_cookies" not in form.errors

        form = forms.HideCookiesForm(data={"hide_cookies": ""})
        assert form.is_valid()
        assert "hide_cookies" not in form.errors

        form = forms.HideCookiesForm(data={"hide_cookies": None})
        assert form.is_valid()
        assert "hide_cookies" not in form.errors
