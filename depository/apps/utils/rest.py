import logging

from rest_framework import status, permissions
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


class GenericAPIException(APIException):
    """
    raises API exceptions with custom messages and custom status codes
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'error'

    def __init__(self, detail, status_code=None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class DepositoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            depository_id = request.META.get('HTTP_DEPOSITORY_ID', None)
            depository_id = int(depository_id)
        except TypeError or ValueError:
            depository_id = None
        if request.user.last_depository is None or request.user.last_depository.code != depository_id:
            raise GenericAPIException(
                detail="There is inconsistency in depository selection, please login again", status_code=468
            )
        return True
