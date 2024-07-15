from django.http import HttpRequest

from .utils import get_cleaned_data_for_step


def show_name_and_business_you_work_for_page(request: HttpRequest) -> bool:
    data = get_cleaned_data_for_step(request, "start")
    return data.get("reporter_professional_relationship") in ("third_party", "no_professional_relationship")
