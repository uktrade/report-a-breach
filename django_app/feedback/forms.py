from typing import Any

from core.forms import BaseModelForm
from crispy_forms_gds.layout import Field, Fieldset, Layout, Size
from django import forms

from .choices import WhatDidNotWorkSoWellChoices
from .crispy_fields import FeedbackStars, HTMLTemplate, get_textarea_field_with_label_id
from .models import FeedbackItem


class FeedbackForm(BaseModelForm):
    what_did_not_work_so_well = forms.MultipleChoiceField(
        choices=WhatDidNotWorkSoWellChoices.choices,
        widget=forms.CheckboxSelectMultiple,
        label="",
        required=False,
    )
    existing_feedback_id = forms.UUIDField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = FeedbackItem
        fields = ("rating", "what_did_not_work_so_well", "how_we_could_improve_the_service")
        labels = {
            "how_we_could_improve_the_service": "How could we improve the service?",
        }

    class Media:
        js = ["feedback/javascript/feedback.js"]
        css = {
            "all": ["feedback/stylesheets/feedback.css"],
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["rating"].choices.pop(0)
        self.helper.layout = Layout(
            FeedbackStars("rating"),
            Fieldset(
                Field.checkboxes("what_did_not_work_so_well", legend=""),
                legend="What did not work so well? (optional)",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
                css_class="optional_question",
            ),
            get_textarea_field_with_label_id(
                "how_we_could_improve_the_service",
                label_id="how_we_could_improve_the_service-label",
                rows=5,
                label_size=Size.MEDIUM,
                label_tag="h2",
                css_class="optional_question",
                max_characters=1200,
                aria_describedby="how_we_could_improve_the_service-label",
            ),
            HTMLTemplate("feedback/feedback_disclaimer.html"),
        )
