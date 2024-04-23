from typing import Union

from django import forms


class BooleanChoiceField(forms.ChoiceField):
    def to_python(self, value: Union[str, bool]) -> Union[str, bool]:
        if isinstance(value, str) and value.lower() in ("false", "0"):
            value = False
        else:
            value = bool(value)
        return value
