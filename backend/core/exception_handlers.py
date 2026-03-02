from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from core.exceptions import ApplicationError


def drf_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return response
    if isinstance(exc, ApplicationError):
        return Response(
            {"message": exc.message, "extra": exc.extra},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return None
