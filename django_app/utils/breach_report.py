from typing import Any

from core.document_storage import PermanentDocumentStorage
from django.forms.models import model_to_dict
from report_a_suspected_breach.choices import TypeOfRelationshipChoices
from report_a_suspected_breach.models import Breach, PersonOrCompany
from utils.companies_house import get_formatted_address
from utils.s3 import get_breach_documents


def get_breach_context_data(breach: Breach) -> dict[str, Any]:
    """Method to return context information of a breach object and its related objects"""
    breach_context = {}

    # Breacher
    if breacher := PersonOrCompany.objects.filter(
        breach_id=breach.id, type_of_relationship=TypeOfRelationshipChoices.breacher
    ).first():
        if breacher.registered_company_number:
            breacher_address = breacher.registered_office_address
        else:
            breacher_address = get_formatted_address(model_to_dict(breacher))
        breach_context["breacher"] = breacher
        breach_context["breacher_address"] = breacher_address

    # Supplier
    if supplier := PersonOrCompany.objects.filter(
        breach_id=breach.id, type_of_relationship=TypeOfRelationshipChoices.supplier
    ).first():
        supplier_address = get_formatted_address(model_to_dict(supplier))
        breach_context["supplier"] = supplier
        breach_context["supplier_address"] = supplier_address

    elif breach.where_were_the_goods_supplied_from == "same_address":
        if breacher:
            breach_context["supplier"] = breacher
            breach_context["supplier_address"] = breacher_address

    # End Users (recipients)
    recipients = PersonOrCompany.objects.filter(breach_id=breach.id, type_of_relationship=TypeOfRelationshipChoices.recipient)
    breach_context["recipients"] = recipients

    # Sanctions Regimes
    sanctions = breach.sanctions_regimes_breached
    breach_context["sanctions"] = sanctions

    # Documents
    upload_documents = get_breach_documents(PermanentDocumentStorage(), str(breach.id))
    breach_context["documents"] = upload_documents

    # Reference
    breach_context["reference"] = breach.reference
    breach_context["reporter_email_address"] = breach.reporter_email_address
    breach_context["breach"] = breach

    return breach_context
