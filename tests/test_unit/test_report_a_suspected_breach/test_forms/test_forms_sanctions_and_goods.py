from unittest.mock import patch

import pytest
from report_a_suspected_breach.forms.forms_sanctions_and_goods import (
    WhenDidYouFirstSuspectForm,
    WhichSanctionsRegimeForm,
)


class TestWhenDidYouFirstSuspectForm:
    def get_date_post_dictionary(self, day: int | None, month: int | None, year: int | None):
        return {"when_did_you_first_suspect_0": day, "when_did_you_first_suspect_1": month, "when_did_you_first_suspect_2": year}

    def test_date_in_the_future(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 3000))
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert (
            form.errors.as_data()["when_did_you_first_suspect"][0].message
            == "The date you first suspected the breach must be in the past"
        )

    def test_year_prefixing(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 20))
        assert form.is_valid()
        assert form.cleaned_data["when_did_you_first_suspect"].year == 2020

    def test_too_short_year(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, 400))
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert form.errors.as_data()["when_did_you_first_suspect"][0].code == "invalid"

    def test_incomplete(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": "exact"} | self.get_date_post_dictionary(1, 1, None))
        assert not form.is_valid()
        assert "when_did_you_first_suspect" in form.errors
        assert form.errors.as_data()["when_did_you_first_suspect"][0].code == "incomplete"

    def test_is_the_date_accurate_required(self):
        form = WhenDidYouFirstSuspectForm(data={"is_the_date_accurate": None})
        assert not form.is_valid()
        assert "is_the_date_accurate" in form.errors
        assert form.errors.as_data()["is_the_date_accurate"][0].code == "required"


@pytest.mark.django_db
class TestWhichSanctionsRegimeForm:
    def test_required(self):
        form = WhichSanctionsRegimeForm(data={"which_sanctions_regime": None})
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.errors.as_data()["which_sanctions_regime"][0].code == "required"

    @patch(
        "report_a_suspected_breach.forms.forms_sanctions_and_goods.get_active_regimes",
        [
            {"name": "test regime", "is_active": True},
            {"name": "test regime1", "is_active": True},
            {"name": "test regime2", "is_active": True},
        ],
    )
    def test_choices_creation(self):
        form = WhichSanctionsRegimeForm()
        assert len(form.fields["which_sanctions_regime"].choices) == 5  # 3 + 2 default choices
        flat_choices = [choice[0] for choice in form.fields["which_sanctions_regime"].choices]
        assert "test regime" in flat_choices
        assert "test regime1" in flat_choices
        assert "test regime2" in flat_choices

        assert flat_choices[-1] == "Other Regime"
        assert flat_choices[-2] == "Unknown Regime"

    @patch(
        "report_a_suspected_breach.forms.forms_sanctions_and_goods.get_active_regimes",
        [
            {"name": "test regime", "is_active": True},
        ],
    )
    def test_assert_unknown_regime_selected_error(self):
        form = WhichSanctionsRegimeForm(data={"which_sanctions_regime": ["Unknown Regime", "test regime"]})
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.errors.as_data()["which_sanctions_regime"][0].code == "invalid"

    @patch(
        "report_a_suspected_breach.forms.forms_sanctions_and_goods.get_active_regimes",
        [
            {"name": "test regime", "is_active": True},
        ],
    )
    def test_assert_other_regime_selected_error(self):
        form = WhichSanctionsRegimeForm(data={"which_sanctions_regime": ["Other Regime", "test regime"]})
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.errors.as_data()["which_sanctions_regime"][0].code == "invalid"
