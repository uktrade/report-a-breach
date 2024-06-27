from typing import Any

from core.document_storage import PermanentDocumentStorage
from django.forms.models import model_to_dict
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import Breach, PersonOrCompany
from utils.companies_house import get_formatted_address
from utils.s3 import get_breach_documents


def get_breach_context_data(context, breach) -> dict[str, Any]:
    """Method to return context information of a breach object and its related objects"""
    # Breach
    context["breach"] = breach

    # Breacher
    if breacher := PersonOrCompany.objects.filter(
        breach_id=breach.id, type_of_relationship=TypeOfRelationshipChoices.breacher
    ).first():
        if breacher.registered_company_number:
            breacher_address = breacher.registered_office_address
        else:
            breacher_address = get_formatted_address(model_to_dict(breacher))
        context["breacher"] = breacher
        context["breacher_address"] = breacher_address

    # Supplier
    if supplier := PersonOrCompany.objects.filter(
        breach_id=breach.id, type_of_relationship=TypeOfRelationshipChoices.supplier
    ).first():
        supplier_address = get_formatted_address(model_to_dict(supplier))
        context["supplier"] = supplier
        context["supplier_address"] = supplier_address

    elif breach.where_were_the_goods_supplied_from == "same_address":
        if breacher:
            context["supplier"] = breacher
            context["supplier_address"] = breacher_address

    # End Users (recipients)
    recipients = PersonOrCompany.objects.filter(breach_id=breach.id, type_of_relationship=TypeOfRelationshipChoices.recipient)
    context["recipients"] = recipients

    # Sanctions Regimes
    sanctions = breach.sanctions_regimes.all()
    context["sanctions"] = sanctions

    # Documents
    upload_documents = get_breach_documents(PermanentDocumentStorage(), str(breach.id))
    context["documents"] = upload_documents

    # Reporter Summary
    summary = breach.tell_us_about_the_suspected_breach
    context["summary"] = summary

    return context


def sort_breaches(sort_str: str, breach_objects: Breach) -> list[Breach]:
    if sort_str == "date of report (newest)":
        sorted_breaches = breach_objects.order_by("-created_by")
    else:
        sorted_breaches = breach_objects.order_by("created_by")
    return sorted_breaches
