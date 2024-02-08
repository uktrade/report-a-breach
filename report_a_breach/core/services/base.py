from time import time

from core.feature_flags import FeatureFlags
from django.conf import settings
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from organisations.models import get_organisation
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from security.constants import SECURITY_GROUP_SUPER_USER
from security.utils import validate_user_case, validate_user_organisation

from config.ratelimit import get_rate
from config.version import __version__

from .exceptions import AccessDenied


@method_decorator(ratelimit(key="user_or_ip", rate=get_rate, method=ratelimit.ALL), name="dispatch")
class ReportABreachApiView(APIView):
    """Base class for all Report A Breach API Views.

    Api responses should always return ResponseSuccess objects if successful, or
    raise an API Exception otherwise.

    The base API class assigns some instance attributes to the
    APIView instance and the response data, in order to conform
    to a standard:

        `start` and `limit` are provided in the response data if
        a queryset attribute is set. In addition _start & _limit
        attributes are set in the APIView object itself.

        _search is set if a `q` query parameter is provided

        `process_time` is set in the response to provide a measure
        of time it took to process this request

        `feature_flags` provides a `FeatureFlag` instance which can be used
        to fetch flags from the SystemParameters. Flag values will be cached
        on the request object, so it can be called multiple times without
        performing multiple queries to the database or cache.
    """

    permission_classes = IsAuthenticated
    allowed_groups = {}

    def __init__(self, *args, **kwargs):
        self.case_id = None
        self.user = None
        self.organisation = None
        self._start = 0
        self._limit = settings.DEFAULT_QUERYSET_PAGE_SIZE
        self._search = None
        self._order_by = ""
        self._order_dir = "asc"
        self.feature_flags = None
        super().__init__(*args, **kwargs)

    def initial(self, request, *args, **kwargs):
        """Initial override.

        Override initial to collect some standard
        request parameters into the API View Object.
        :param (HttpRequest) request: Request object.
        """
        super().initial(request, *args, **kwargs)
        organisation_id = kwargs.get("organisation_id")
        self.case_id = kwargs.get("case_id")
        self.user = request.user
        self.organisation = get_organisation(organisation_id)
        if self.organisation:
            self.organisation.set_user_context(request.user)
        if self.allowed_groups:
            self.raise_on_invalid_access()
        self._start = int(request.query_params.get("start", 0))
        self._limit = int(request.query_params.get("limit", settings.DEFAULT_QUERYSET_PAGE_SIZE))
        self._search = request.query_params.get("q")
        self._order_by = request.query_params.get("order_by")
        self._order_dir = request.query_params.get("order_dir", "asc")

    def raise_on_invalid_access(self):
        """Check user organisation authorisation.

        Raise an AccessDenied API exception if the user is not allowed to
        access the organisation.
        """
        is_valid = False
        org_id = self.organisation.id if self.organisation else None
        if self.user.has_group(SECURITY_GROUP_SUPER_USER):
            is_valid = True
        elif self.allowed_groups.get(self.request.method) and self.user.has_groups(
            self.allowed_groups[self.request.method]
        ):
            is_valid = True
        elif self.case_id and org_id:
            is_valid = validate_user_case(self.user, self.case_id, org_id)
        elif org_id:
            is_valid = validate_user_organisation(self.user, org_id)
        if not is_valid:
            raise AccessDenied("User does not have access to organisation")

    def dispatch(self, request, *args, **kwargs):
        """Dispatch override.

        :param (HttpRequest) request: Request object.
        """
        time_recv = time()
        self.feature_flags = FeatureFlags()
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(response, "data"):
            if response.exception is True:
                response["error"] = True
                if settings.DEBUG:
                    # logger.error(f"Error: {response.data}") TODO: require messge?
                    pass
            else:
                response.data["version"] = __version__
                response.data["process_time"] = time() - time_recv
                if hasattr(self, "queryset"):
                    response.data["start"] = self._start
                    response.data["limit"] = self._limit
        return response

    def validate_required_fields(self, request):
        if hasattr(self, "required_keys"):
            missing_keys = [key for key in self.required_keys if not request.data.get(key)]
            return missing_keys
        return []

    @property
    def sort_spec(self):
        if self._order_by and self._order_dir:
            order_dir_indicator = "-" if self._order_dir == "desc" else ""
            return [f"{order_dir_indicator}{self._order_by}"]
        return None


class ResponseSuccess(Response):
    """Common response object.

    Manages a standard response format for all API calls.
    """

    def __init__(self, data=None, http_status=None, content_type=None):
        _status = http_status or status.HTTP_200_OK
        data = data or {}
        reply = {"response": {"success": True}}
        reply["response"].update(data)
        super().__init__(data=reply, status=_status, content_type=content_type)
