from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, PermissionDenied, ValidationError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(exc, ValidationError):
        detail = response.data
        if isinstance(detail, list):
            errors = {"non_field_errors": detail}
        elif isinstance(detail, dict):
            errors = detail
        else:
            errors = {"non_field_errors": [str(detail)]}
        response.data = {"message": "Validation failed.", "errors": errors}
        return response

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        detail = response.data.get("detail", "Authentication failed.")
        response.data = {"message": "Authentication failed.", "errors": {"auth": [str(detail)]}}
        return response

    if isinstance(exc, PermissionDenied) or response.status_code == status.HTTP_403_FORBIDDEN:
        detail = response.data.get("detail", "Permission denied.")
        response.data = {"message": "Permission denied.", "errors": {"permission": [str(detail)]}}
        return response

    if isinstance(response.data, dict) and "detail" in response.data:
        detail = response.data["detail"]
        response.data = {"message": str(detail), "errors": {"non_field_errors": [str(detail)]}}
        return response

    return response
