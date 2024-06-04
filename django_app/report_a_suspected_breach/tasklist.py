from functools import cached_property
from typing import Iterable

from django.views import View

from . import forms


class Task:
    form_steps = {}
    name = ""
    hint_text = ""
    show_on_tasklist = True

    def __init__(self, wizard_view: View, task_list: list["Task"]) -> None:
        super().__init__()
        self.wizard_view = wizard_view
        self.task_list = task_list

    @property
    def optional_steps(self) -> set:
        return set()

    @property
    def non_wizard_steps(self) -> set:
        return set()

    @property
    def underscored_task_name(self) -> str:
        return self.name.lower().replace(" ", "_")

    @cached_property
    def status(self) -> str:
        if self.complete:
            return "Completed"
        elif self.can_start:
            return "Not yet started"
        return "Cannot start yet"

    def start_url(self) -> str:
        return self.wizard_view.get_step_url([*self.form_steps.keys()][0])

    @cached_property
    def can_start(self) -> bool:
        """If the last task is complete and this one isn't, this task can be started"""
        if self.task_list.tasks[self.task_list.tasks.index(self) - 1].complete and not self.complete:
            return True
        else:
            return False

    @cached_property
    def complete(self) -> bool:
        """Check if all the steps in this task have been completed.

        However, sometime steps within this task may be optional, so we need to apply the conditional display logic
        found in the form_step_conditions.py file to determine if the step is optional for the user."""

        # Get the steps that have been completed in this task
        completed_steps = set(
            [step_name for step_name, _ in self.form_steps.items() if self.wizard_view.storage.get_step_data(step_name)]
        )

        # get a set of the steps that are missing
        missing_steps = set(self.form_steps.keys()) - completed_steps

        if not missing_steps:
            # if all steps are completed, then by definition the entire task is complete.
            # don't bother with the rest of the logic
            return True

        # figure out if these missing steps are compulsory or optional or not part of wizard
        compulsory_steps = {*self.wizard_view.get_form_list().keys()} - self.optional_steps - self.non_wizard_steps

        # find the intersection between compulsory_steps and missing_steps. If it exists, the task is not complete
        if compulsory_steps.intersection(missing_steps):
            return False
        else:
            return True


class YourDetailsTask(Task):
    form_steps = {
        "start": forms.StartForm,
        "email": forms.EmailForm,
        "verify": forms.EmailVerifyForm,
        "name": forms.NameForm,
        "name_and_business_you_work_for": forms.NameAndBusinessYouWorkForForm,
    }
    name = "Your details"
    non_wizard_steps = {"verify"}

    @cached_property
    def can_start(self) -> bool:
        """This is the first task, can always start unless it's already complete"""
        if self.complete:
            return False
        else:
            return True


class AboutThePersonOrBusinessTask(Task):
    form_steps = {
        "are_you_reporting_a_business_on_companies_house": forms.AreYouReportingABusinessOnCompaniesHouseForm,
        "do_you_know_the_registered_company_number": forms.DoYouKnowTheRegisteredCompanyNumberForm,
        "check_company_details": forms.SummaryForm,
        "where_is_the_address_of_the_business_or_person": forms.WhereIsTheAddressOfTheBusinessOrPersonForm,
        "business_or_person_details": forms.BusinessOrPersonDetailsForm,
    }
    name = "About the person or business you're reporting"
    hint_text = "Contact details"


class OverviewOfTheSuspectedBreachTask(Task):
    form_steps = {
        "when_did_you_first_suspect": forms.WhenDidYouFirstSuspectForm,
        "which_sanctions_regime": forms.WhichSanctionsRegimeForm,
        "what_were_the_goods": forms.WhatWereTheGoodsForm,
    }
    name = "Overview of the suspected breach"
    hint_text = "Which sanctions were breached, and what were the goods or services"


class TheSupplyChainTask(Task):
    form_steps = {
        "where_were_the_goods_supplied_from": forms.WhereWereTheGoodsSuppliedFromForm,
        "about_the_supplier": forms.AboutTheSupplierForm,
        "where_were_the_goods_made_available_from": forms.WhereWereTheGoodsMadeAvailableForm,
        "where_were_the_goods_supplied_to": forms.WhereWereTheGoodsSuppliedToForm,
        "where_were_the_goods_made_available_to": forms.WhereWereTheGoodsMadeAvailableToForm,
        "about_the_end_user": forms.AboutTheEndUserForm,
        "end_user_added": forms.EndUserAddedForm,
        "were_there_other_addresses_in_the_supply_chain": forms.WereThereOtherAddressesInTheSupplyChainForm,
    }
    name = "The supply chain"
    hint_text = "Contact details for the supplier, end-user and anyone else in the supply chain"
    optional_steps = {"about_the_end_user", "end_user_added"}


class SanctionsBreachDetailsTask(Task):
    form_steps = {
        "upload_documents": forms.UploadDocumentsForm,
        "tell_us_about_the_suspected_breach": forms.TellUsAboutTheSuspectedBreachForm,
    }
    name = "Sanctions breach details"
    hint_text = "Upload documents and give any additional information"
    optional_steps = {"upload_documents"}


class SummaryAndDeclaration(Task):
    show_on_tasklist = False
    form_steps = {
        "summary": forms.SummaryForm,
        "declaration": forms.DeclarationForm,
    }


class TaskList:
    def __init__(self, tasks: Iterable, wizard_view: View) -> None:
        super().__init__()
        self.wizard_view = wizard_view
        self.tasks = [task(wizard_view, self) for task in tasks]

    def __iter__(self) -> Iterable[Task]:
        return iter(self.tasks)

    @cached_property
    def current_task(self) -> Task | None:
        """Get the current task object based on the current step in the wizard."""
        return self.get_task_from_step_name(self.wizard_view.steps.current)

    def should_show_task_list_page(self) -> bool:
        """Should the user be shown the tasklist page.

        Have they just started a new task?, or have they completed all tasks?"""
        """Check if the user has just started a new task. If so then show them the tasklist page"""
        if current_task := self.current_task:
            return self.wizard_view.steps.current == [*current_task.form_steps.keys()][0]

        return False

    def get_task_from_step_name(self, step_name: str) -> Task | None:
        """Helper function to get the task object based on the step name."""
        for task in self.tasks:
            if step_name in task.form_steps:
                return task
        return None

    def complete(self) -> bool:
        """Check if all the tasks are complete."""
        return all(task.complete if task.show_on_tasklist else True for task in self.tasks)


def get_tasklist(wizard_view: View) -> TaskList:
    return TaskList(
        tasks=(
            YourDetailsTask,
            AboutThePersonOrBusinessTask,
            OverviewOfTheSuspectedBreachTask,
            TheSupplyChainTask,
            SanctionsBreachDetailsTask,
            SummaryAndDeclaration,
        ),
        wizard_view=wizard_view,
    )


def get_blocked_tasks(wizard_view: View) -> list["Task"]:
    tasks = get_tasklist(wizard_view=wizard_view)
    current_task = tasks.current_task
    task_list = tasks.tasks
    current_index = task_list.index(current_task)
    if current_task != len(task_list) - 1:
        blocked_tasks = [task for task in tasks if task_list.index(task) > current_index and not task.can_start]
        return blocked_tasks
    return []
