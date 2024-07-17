from core.views import BaseFormView
from django.urls import reverse_lazy
from report_a_suspected_breach import forms


class WhenDidYouFirstSuspectView(BaseFormView):
    form_class = forms.WhenDidYouFirstSuspectForm
    success_url = reverse_lazy("report_a_suspected_breach:which_sanctions_regime")


class WhichSanctionsRegimeView(BaseFormView):
    form_class = forms.WhichSanctionsRegimeForm
    template_name = "report_a_suspected_breach/form_steps/which_sanctions_regimes.html"
    success_url = reverse_lazy("report_a_suspected_breach:what_were_the_goods")


class WhatWereTheGoodsView(BaseFormView):
    form_class = forms.WhatWereTheGoodsForm
    success_url = reverse_lazy(
        "report_a_suspected_breach:tasklist_with_current_task", kwargs={"current_task_name": "supply_chain"}
    )
