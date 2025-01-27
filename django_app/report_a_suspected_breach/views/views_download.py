from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from playwright.sync_api import sync_playwright
from report_a_suspected_breach.models import Breach

from django_app.utils import breach_report


class DownloadPDFView(DetailView):
    # TODO: update the template when DST-797 is complete
    template_name = "report_a_suspected_breach/form_steps/report_pdf.html"

    def get_object(self, queryset=None) -> Breach:
        self.breach = get_object_or_404(Breach, reference=self.request.GET.get("reference", ""))
        return self.breach

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context_data = self.get_context_data(**kwargs)
        filename = f"report-{context_data['reference']}.pdf"
        pdf_data = None
        template_string = render_to_string(self.template_name, context=context_data)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(mark_safe(template_string))
            pdf_data = page.pdf(format="A4")
            browser.close()

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={filename}"

        return response

    def get_context_data(self, *args: object, **kwargs: object) -> dict[str, Any]:
        # self.object = self.get_object()
        self.object = get_object_or_404(Breach, reference=self.request.GET.get("reference", ""))
        context = super().get_context_data(**kwargs)
        breach_context_data = breach_report.get_breach_context_data(self.object)
        context.update(breach_context_data)
        context["reference"] = self.request.GET.get("reference", "")
        context["email"] = self.request.session.get("email", {}).get("reporter_email_address", "")
        context["reporter_name"] = self.request.session.get("reporter_full_name", "")
        context["relationship"] = self.request.session.get("reporter_professional_relationship", "")
        if (
            self.request.session.get("do_you_know_the_registered_company_number", {}).get(
                "do_you_know_the_registered_company_number"
            )
            == "yes"
        ):
            registered_company_number = self.request.session.get("do_you_know_the_registered_company_number").get(
                "registered_company_number"
            )
        else:
            registered_company_number = "Not provided"
        context["registered_company_number"] = registered_company_number
        context["company_name"] = self.request.session.get("company_details", {}).get("name", "")
        context["company_address"] = self.request.session.get("company_details", {}).get("readable_address", "")
        # context["when_did_you_suspect"] = when_did_you_first_suspect
        # context["sanctions_breached"]
        # context["what_were_the_goods"]
        # context["supplier_details"]
        # context["end_users"]
        # context["supporting_documents"]
        # context["breach_summary"]
        return context
