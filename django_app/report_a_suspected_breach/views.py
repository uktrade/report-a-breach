import uuid

from core.decorators import cached_classproperty
from core.document_storage import PermanentDocumentStorage, TemporaryDocumentStorage
from core.views import BaseWizardView
from django.conf import settings
from django.contrib.sessions.models import Session
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView
from utils.companies_house import get_formatted_address
from utils.notifier import send_email
from utils.s3 import generate_presigned_url

from .choices import TypeOfRelationshipChoices
from .models import Breach, PersonOrCompany, ReporterEmailVerification, SanctionsRegime
from .tasklist import (
    AboutThePersonOrBusinessTask,
    OverviewOfTheSuspectedBreachTask,
    SanctionsBreachDetailsTask,
    SummaryAndDeclaration,
    TheSupplyChainTask,
    YourDetailsTask,
    get_tasklist,
)


class ReportABreachWizardView(BaseWizardView):
    template_names_lookup = {
        "summary": "report_a_suspected_breach/form_steps/summary.html",
        "check_company_details": "report_a_suspected_breach/form_steps/check_company_details.html",
        "end_user_added": "report_a_suspected_breach/form_steps/end_user_added.html",
        "declaration": "report_a_suspected_breach/form_steps/declaration.html",
    }
    template_name = "report_a_suspected_breach/generic_form_step.html"
    storage_name = "report_a_suspected_breach.session.SessionStorage"
    file_storage = TemporaryDocumentStorage()

    @cached_classproperty
    def form_list(cls):
        task_list = (
            YourDetailsTask,
            AboutThePersonOrBusinessTask,
            OverviewOfTheSuspectedBreachTask,
            TheSupplyChainTask,
            SanctionsBreachDetailsTask,
            SummaryAndDeclaration,
        )
        unpacked = []
        for task in task_list:
            for step_name, step_form in task.form_steps.items():
                unpacked.append((step_name, step_form))

        return unpacked

    def get(self, request, *args, **kwargs):
        if "reset" in self.request.GET:
            for step_name, _ in self.form_list.items():
                # clearing the lru_cache for get_cleaned_data_for_step
                if self.get_cleaned_data_for_step.has(step_name):
                    self.get_cleaned_data_for_step.delete(step_name)
            self.storage.reset()
            self.storage.current_step = self.steps.first

        if request.resolver_match.url_name == "about_the_end_user":
            # we want to add another end-user, we need to ask the user if the new end-user is in the UK or not
            if "end_user_uuid" not in self.request.resolver_match.kwargs:
                default_redirect = "where_were_the_goods_supplied_to"
                if self.request.session.get("made_available_journey"):
                    default_redirect = "where_were_the_goods_made_available_to"
                self.storage.current_step = default_redirect
                kwargs["step"] = default_redirect
                return super().get(request, *args, **kwargs)
            else:
                # we're trying to edit an existing end-user, so we need to load the form with the existing data
                self.storage.current_step = "about_the_end_user"
                return super().get(request, *args, step="about_the_end_user", **kwargs)

        if request.resolver_match.url_name == "where_were_the_goods_supplied_to":
            self.storage.current_step = "where_were_the_goods_supplied_to"
            return super().get(request, *args, step="where_were_the_goods_supplied_to", **kwargs)

        if request.resolver_match.url_name == "where_were_the_goods_made_available_to":
            self.storage.current_step = "where_were_the_goods_made_available_to"
            return super().get(request, *args, step="where_were_the_goods_made_available_to", **kwargs)

        # before we initialise the tasklit, we need to make sure the current_step is correct
        if step_url := kwargs.get("step", None):
            if step_url in self.get_form_list():
                self.storage.current_step = step_url

        # check if the user has completed a task, if so, redirect them to the tasklist
        # the exception to this is if the user wants to explicitly start the next task, in which case we should let them
        # or, if they're trying to change their answers from the summary page
        self.tasklist = get_tasklist(self)
        if (
            not request.GET.get("start", "") == "true"
            and not request.session.get("redirect") == "summary"
            and not request.GET.get("redirect", "") == "summary"
            and self.tasklist.should_show_task_list_page()
        ):
            return render(request, "report_a_suspected_breach/tasklist.html", context={"tasklist": self.tasklist, "view": self})

        return super().get(request, *args, **kwargs)

    def get_step_url(self, step):
        if step == "about_the_end_user" and "end_user_uuid" in self.kwargs:
            return reverse(
                "report_a_suspected_breach:about_the_end_user",
                kwargs={"end_user_uuid": self.kwargs["end_user_uuid"]},
            )

        if step == "where_were_the_goods_supplied_to" and "end_user_uuid" in self.kwargs:
            return reverse(
                "report_a_suspected_breach:where_were_the_goods_supplied_to",
                kwargs={"end_user_uuid": self.kwargs["end_user_uuid"]},
            )

        if step == "where_were_the_goods_made_available_to" and "end_user_uuid" in self.kwargs:
            return reverse(
                "report_a_suspected_breach:where_were_the_goods_made_available_to",
                kwargs={"end_user_uuid": self.kwargs["end_user_uuid"]},
            )
        return super().get_step_url(step)

    def render_next_step(self, form, **kwargs):
        if self.steps.current == "end_user_added" and form.cleaned_data["do_you_want_to_add_another_end_user"]:
            default_path = "where_were_the_goods_supplied_to"
            if self.request.session.get("made_available_journey"):
                default_path = "where_were_the_goods_made_available_to"

            # we want to redirect them to 'where is the end user' page, but pass another query parameter to indicate that they
            # know about another end-user, so we can remove the last option 'I don't know' from the list of options
            return redirect(f"{self.get_step_url(default_path)}?add_another_end_user=yes")

        if self.steps.current == "where_were_the_goods_made_available_from":
            # we don't want to call super() here as that appears to be calling the next item in the form list
            # rather than applying the condition logic
            if form.cleaned_data["where_were_the_goods_made_available_from"] in ["different_uk_address", "outside_the_uk"]:
                return redirect(self.get_step_url("about_the_supplier"))
            elif form.cleaned_data["where_were_the_goods_made_available_from"] in ["same_address", "i_do_not_know"]:
                return redirect(self.get_step_url("where_were_the_goods_made_available_to"))
        return super().render_next_step(form, **kwargs)

    def get_summary_context_data(self, form, context):
        """Collects all the nice form data and puts it into a dictionary for the summary page. We need to check if
        a lot of this data is present, as the user may have skipped some steps, so we import the form_step_conditions
        that are used to determine if a step should be shown, this is to avoid duplicating the logic here."""

        # we're importing these methods here to avoid circular imports
        from .form_step_conditions import (
            show_check_company_details_page_condition,
            show_name_and_business_you_work_for_page,
        )

        cleaned_data = self.get_all_cleaned_data()
        context["form_data"] = cleaned_data
        context["is_company_obtained_from_companies_house"] = show_check_company_details_page_condition(self)
        context["is_third_party_relationship"] = show_name_and_business_you_work_for_page(self)
        context["is_made_available_journey"] = self.request.session.get("made_available_journey")
        if uploaded_file := context["form_data"]["upload_documents"]["documents"]:
            presigned_url = generate_presigned_url(TemporaryDocumentStorage().bucket.meta.client, uploaded_file.file.obj)
            context["form_data"]["upload_documents"]["url"] = presigned_url
        if end_users := self.request.session.get("end_users", None):
            context["form_data"]["end_users"] = end_users

        if (
            self.get_cleaned_data_for_step("where_were_the_goods_supplied_from").get("where_were_the_goods_supplied_from")
            == "same_address"
        ):
            if show_check_company_details_page_condition(self):
                registered_company = context["form_data"]["do_you_know_the_registered_company_number"]
                context["form_data"]["about_the_supplier"] = {}
                context["form_data"]["about_the_supplier"]["name"] = registered_company["registered_company_name"]
                context["form_data"]["about_the_supplier"]["readable_address"] = registered_company["registered_office_address"]
            else:
                context["form_data"]["about_the_supplier"] = context["form_data"]["business_or_person_details"]
        return context

    def process_are_you_reporting_a_business_on_companies_house_step(self, form):
        """We want to clear the company details from the session if the user selects anything but 'yes', if they do
        select 'yes' then we want to delete the step data for the next step(s) in the chain of conditionals."""
        if form.cleaned_data["business_registered_on_companies_house"] != "yes":
            self.request.session.pop("company_details", None)
            self.request.session.modified = True
        else:
            self.storage.delete_step_data("where_is_the_address_of_the_business_or_person", "business_or_person_details")

        return self.get_form_step_data(form)

    def process_about_the_end_user_step(self, form):
        current_end_users = self.request.session.get("end_users", {})

        end_user_uuid = self.kwargs.get("end_user_uuid", str(uuid.uuid4()))
        # want to save both the cleaned data (for rendering to the user in the summary page) and the dirty data
        # (for re-instantiating the form in the case of a user wanting to change their input)
        current_end_users[end_user_uuid] = {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }
        self.request.session["end_users"] = current_end_users
        self.request.session.modified = True
        return self.get_form_step_data(form)

    def process_do_you_know_the_registered_company_number_step(self, form):
        self.request.session.pop("company_details", None)
        self.request.session.modified = True

        if form.cleaned_data.get("do_you_know_the_registered_company_number") == "yes":
            self.request.session["company_details"] = form.cleaned_data

        return self.get_form_step_data(form)

    def process_email_step(self, form):
        reporter_email_address = form.cleaned_data.get("reporter_email_address")
        verify_code = get_random_string(6, allowed_chars="0123456789")
        user_session = Session.objects.get(session_key=self.request.session.session_key)
        ReporterEmailVerification.objects.create(
            reporter_session=user_session,
            email_verification_code=verify_code,
        )
        print(verify_code)
        send_email(
            email=reporter_email_address,
            context={"verification_code": verify_code},
            template_id=settings.EMAIL_VERIFY_CODE_TEMPLATE_ID,
        )
        return self.get_form_step_data(form)

    def process_upload_documents_form(self, form):
        """Overriding this method to store the file name in the session, so we can use it later."""
        if form.is_valid():
            self.request.session["uploaded_file_name"] = form.cleaned_data["file"].name
            self.request.session.modified = True
        return super().process_step(form)

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        kwargs["request"] = self.request

        if step == "business_or_person_details":
            where_is_the_address = (
                self.get_cleaned_data_for_step("where_is_the_address_of_the_business_or_person").get("where_is_the_address")
                == "in_the_uk"
            )
            do_you_know_the_registered_company_number = (
                self.get_cleaned_data_for_step("do_you_know_the_registered_company_number").get(
                    "do_you_know_the_registered_company_number"
                )
                == "no"
            )
            if where_is_the_address or do_you_know_the_registered_company_number:
                kwargs["is_uk_address"] = "in_the_uk"

        if step == "about_the_supplier":
            where_were_the_goods_supplied_from = (self.get_cleaned_data_for_step("where_were_the_goods_supplied_from") or {}).get(
                "where_were_the_goods_supplied_from", ""
            )
            if where_were_the_goods_supplied_from:
                is_uk_address = where_were_the_goods_supplied_from == "different_uk_address"
                kwargs["is_uk_address"] = is_uk_address
            where_were_the_goods_made_available_from = (
                self.get_cleaned_data_for_step("where_were_the_goods_made_available_from") or {}
            ).get("where_were_the_goods_made_available_from", "")
            if where_were_the_goods_made_available_from:
                is_uk_address = where_were_the_goods_made_available_from == "different_uk_address"
                kwargs["is_uk_address"] = is_uk_address

        if step == "about_the_end_user":
            where_were_the_goods_supplied_to = (self.get_cleaned_data_for_step("where_were_the_goods_supplied_to") or {}).get(
                "where_were_the_goods_supplied_to", ""
            )
            if where_were_the_goods_supplied_to:
                is_uk_address = where_were_the_goods_supplied_to == "in_the_uk"
                kwargs["is_uk_address"] = is_uk_address

            where_were_the_goods_made_available_to = (
                self.get_cleaned_data_for_step("where_were_the_goods_made_available_to") or {}
            ).get("where_were_the_goods_made_available_to", "")
            if where_were_the_goods_made_available_to:
                is_uk_address = where_were_the_goods_made_available_to == "in_the_uk"
                kwargs["is_uk_address"] = is_uk_address

        if step in (
            "where_were_the_goods_supplied_from",
            "where_were_the_goods_made_available_from",
        ):
            from .form_step_conditions import show_check_company_details_page_condition

            obtained_from_companies_house = show_check_company_details_page_condition(self)
            if obtained_from_companies_house:
                address_string = self.get_cleaned_data_for_step("do_you_know_the_registered_company_number").get(
                    "registered_office_address"
                )
            else:
                address_string = get_formatted_address(self.get_cleaned_data_for_step("business_or_person_details"))

            kwargs["address_string"] = address_string

        return kwargs

    def store_documents_in_s3(self) -> None:
        """
        Copies documents from the default temporary storage to permanent storage on s3
        """
        if uploaded_docs := self.storage.get_step_files("upload_documents"):
            permanent_storage_bucket = PermanentDocumentStorage()
            files = uploaded_docs["upload_documents-documents"]

            object_key = f"{self.request.session.session_key}/{files.name}"

            try:
                permanent_storage_bucket.bucket.meta.client.copy(
                    CopySource={"Bucket": settings.TEMPORARY_S3_BUCKET_NAME, "Key": object_key},
                    Bucket=settings.PERMANENT_S3_BUCKET_NAME,
                    Key=object_key,
                    SourceClient=self.file_storage.bucket.meta.client,
                )
            except Exception:
                # todo - AccessDenied when copying from temporary to permanent bucket when deployed - investigate
                pass

    def save_person_or_company_to_db(
        self, breach: Breach, person_or_company: dict[str, str], relationship: TypeOfRelationshipChoices
    ) -> None:
        new_business_or_person_details = PersonOrCompany.objects.create(
            person_or_company="",
            name=person_or_company.get("name", ""),
            website=person_or_company.get("website"),
            address_line_1=person_or_company.get("address_line_1"),
            address_line_2=person_or_company.get("address_line_2"),
            address_line_3=person_or_company.get("address_line_3"),
            address_line_4=person_or_company.get("address_line_4"),
            town_or_city=person_or_company.get("town_or_city"),
            country=person_or_company.get("country"),
            county=person_or_company.get("county"),
            postal_code=person_or_company.get("postal_code", ""),
            breach=breach,
            type_of_relationship=relationship,
        )
        new_business_or_person_details.save()

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        self.store_documents_in_s3()

        # we're importing these methods here to avoid circular imports
        from .form_step_conditions import (
            show_about_the_supplier_page,
            show_check_company_details_page_condition,
            show_name_and_business_you_work_for_page,
        )

        if show_name_and_business_you_work_for_page(self):
            reporter_full_name = cleaned_data["name_and_business_you_work_for"]["reporter_full_name"]
            reporter_name_of_business_you_work_for = cleaned_data["name_and_business_you_work_for"][
                "reporter_name_of_business_you_work_for"
            ]
        else:
            reporter_full_name = cleaned_data["name"]["reporter_full_name"]
            business_or_person_details_step = cleaned_data.get("business_or_person_details", {})
            reporter_name_of_business_you_work_for = business_or_person_details_step.get("name", "")

        do_you_know_the_registered_company_number_step = cleaned_data.get("do_you_know_the_registered_company_number", {})
        do_you_know_the_registered_company_number = do_you_know_the_registered_company_number_step.get(
            "do_you_know_the_registered_company_number", ""
        )
        registered_company_number = do_you_know_the_registered_company_number_step.get("registered_company_number", "")

        user_session = Session.objects.get(session_key=self.request.session.session_key)
        reporter_email_verification = ReporterEmailVerification.objects.get(
            reporter_session_id=user_session, email_verification_code=cleaned_data["verify"]["email_verification_code"]
        )
        print(cleaned_data)

        # Save Breach to Database
        new_breach = Breach.objects.create(
            reporter_professional_relationship=cleaned_data["start"]["reporter_professional_relationship"],
            reporter_email_address=cleaned_data["email"]["reporter_email_address"],
            reporter_email_verification=reporter_email_verification,
            reporter_full_name=reporter_full_name,
            reporter_name_of_business_you_work_for=reporter_name_of_business_you_work_for,
            when_did_you_first_suspect=cleaned_data["when_did_you_first_suspect"]["when_did_you_first_suspect"],
            is_the_date_accurate=cleaned_data["when_did_you_first_suspect"]["is_the_date_accurate"],
            # additional_information="",
            what_were_the_goods=cleaned_data["what_were_the_goods"]["what_were_the_goods"],
            business_registered_on_companies_house=cleaned_data["are_you_reporting_a_business_on_companies_house"][
                "business_registered_on_companies_house"
            ],
            do_you_know_the_registered_company_number=do_you_know_the_registered_company_number,
            registered_company_number=registered_company_number,
            were_there_other_addresses_in_the_supply_chain=cleaned_data["were_there_other_addresses_in_the_supply_chain"][
                "were_there_other_addresses_in_the_supply_chain"
            ],
            other_addresses_in_the_supply_chain=cleaned_data["were_there_other_addresses_in_the_supply_chain"][
                "other_addresses_in_the_supply_chain"
            ],
            tell_us_about_the_suspected_breach=cleaned_data["tell_us_about_the_suspected_breach"][
                "tell_us_about_the_suspected_breach"
            ],
        )

        if declared_sanctions := cleaned_data["which_sanctions_regime"]["which_sanctions_regime"]:
            for sanction in declared_sanctions:
                if sanction == "unknown_regime":
                    new_breach.unknown_sanctions_regime = True
                if sanction == "other_regime":
                    new_breach.other_sanctions_regime = True
            sanctions_regimes = SanctionsRegime.objects.filter(full_name__in=declared_sanctions)
            new_breach.sanctions_regimes.set(sanctions_regimes)

        new_reference = new_breach.assign_reference()
        new_breach.save()

        # Save Breacher Details to Database
        if not show_check_company_details_page_condition(self):
            breacher_details = cleaned_data["business_or_person_details"]
            self.save_person_or_company_to_db(new_breach, breacher_details, TypeOfRelationshipChoices.breacher)

        # Save Supplier Details to Database
        if show_about_the_supplier_page(self):
            supplier_details = cleaned_data["about_the_supplier"]
            self.save_person_or_company_to_db(new_breach, supplier_details, TypeOfRelationshipChoices.supplier)

        # Save Recipient(s) Details to Database
        if end_users := self.request.session.get("end_users", None):
            for end_user in end_users:
                end_user_details = end_users[end_user]["cleaned_data"]
                self.save_person_or_company_to_db(new_breach, end_user_details, TypeOfRelationshipChoices.recipient)

        self.request.session.pop("end_users", None)
        self.request.session.pop("made_available_journey", None)
        self.request.session.modified = True
        self.request.session["reference_id"] = new_reference
        self.storage.reset()
        self.storage.current_step = self.steps.first
        return redirect(reverse("report_a_suspected_breach:complete"))


class CompleteView(TemplateView):
    template_name = "report_a_suspected_breach/complete.html"
