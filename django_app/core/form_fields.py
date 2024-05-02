from django import forms


class BooleanChoiceField(forms.ChoiceField):

    @staticmethod
    def to_python(value: str | bool) -> bool:
        if isinstance(value, str) and value.lower() in ("false", "0"):
            value = False
        else:
            value = bool(value)
        return value
