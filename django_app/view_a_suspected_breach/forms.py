from core.forms import BaseModelForm

from .models import AdminUser

# from crispy_forms_gds.choices import Choice
# from crispy_forms_gds.layout import (
#     ConditionalQuestion,
#     ConditionalRadios,
#     Field,
#     Fieldset,
#     Fluid,
#     Layout,
#     Size,
# )
# from django import forms


class AdminStartForm(BaseModelForm):
    class Meta:
        model = AdminUser
