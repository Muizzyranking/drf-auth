from django.core.signing import TimestampSigner
from django.template.loader import render_to_string
from rest_framework.request import Request
from rest_framework.views import Response, exception_handler

from accounts.models import User

signer = TimestampSigner()


def send_verification_email(request: Request, user: User) -> str:
    """
    Sends verification email to user if the user has a valid email.

    Args:
        request: The request object
        user: The user object
    """
    try:
        token = signer.sign(user.pk)
        scheme = request.scheme
        host = request.get_host()
        url = f"{scheme}://{host}/api/auth/confirm-email/{token}"

        subject = "Verify your email"
        html_message = render_to_string("email/verify.html", {"url": url})
        user.send_email(subject=subject, html_message=html_message)
        return token
    except Exception as e:
        raise e


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response({"message": "Not Found"}, status=404)
    return response
