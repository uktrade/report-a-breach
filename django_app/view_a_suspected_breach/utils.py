from django.conf import settings


def craft_view_a_suspected_breach_url(path: str) -> str:
    """Crafts and returns a full, complete URL for a path in the view_a_licence_app."""
    return f"{settings.PROTOCOL}{settings.VIEW_A_SUSPECTED_BREACH_DOMAIN}{path}"


def get_view_a_suspected_breach_url(reference: str) -> str:
    return craft_view_a_suspected_breach_url(f"/view/view-report/{reference}/")
