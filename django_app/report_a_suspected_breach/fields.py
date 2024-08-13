from datetime import date
from typing import Any, List

from crispy_forms_gds.fields import DateInputField as CrispyDateInputField
from crispy_forms_gds.widgets import DateInputWidget
from django import forms
from django.core.files.uploadedfile import UploadedFile


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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.__class__.__name__ = "ClearableFileInput"


class MultipleFileField(forms.FileField):
    def __init__(self, *args: object, **kwargs: object) -> None:
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data: list[UploadedFile], initial: UploadedFile | None = None) -> list[UploadedFile] | UploadedFile:
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class DefaultChoiceField(forms.ChoiceField):
    """A ChoiceField that validates particular values as always okay despite not being in the choices."""

    def validate(self, value: Any) -> None:
        if value not in self.empty_values and not self.valid_value(value):
            raise forms.ValidationError(self.error_messages["invalid_choice"], code="invalid_choice")

    def valid_value(self, value):
        """Check to see if the provided value is a valid choice."""
        if value in self.valid_values:
            return True
        return super().valid_value(value)

    def __init__(self, *args: object, valid_values: list[str], **kwargs: object) -> None:
        self.valid_values = valid_values
        super().__init__(*args, **kwargs)
