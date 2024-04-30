from datetime import date
from typing import Any, List

from crispy_forms_gds.fields import DateInputField as CrispyDateInputField
from crispy_forms_gds.widgets import DateInputWidget
from django import forms


class DateInputField(forms.MultiValueField):
    widget = DateInputWidget

    def __init__(self, *args: object, **kwargs: object) -> None:
        fields = (
            forms.CharField(
                label="Day",
            ),
            forms.CharField(
                label="Month",
            ),
            forms.CharField(
                label="Year",
            ),
        )

        super().__init__(fields=fields, **kwargs)

    def clean(self, value: List[Any]) -> date | None:
        if any(value) and not all(value):
            raise forms.ValidationError(self.error_messages["incomplete"], code="incomplete")

        return CrispyDateInputField.clean(self, value)

    def compress(self, data_list: List[int]) -> date | None:
        day, month, year = data_list
        if day and month and year:
            if len(year) == 2:
                year = f"20{year}"

            if len(year) < 4:
                raise forms.ValidationError(self.error_messages["invalid"], code="invalid")

            try:
                return date(day=int(day), month=int(month), year=int(year))
            except ValueError:
                raise forms.ValidationError(self.error_messages["invalid"], code="invalid")
        else:
            return None
