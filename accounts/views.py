from typing import Dict

from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.schemas import (
    confirm_email_schema,
    login_schema,
    refresh_token_schema,
    resend_verification_email_schema,
    signup_schema,
)
from accounts.serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    SignUpSerializer,
)
from accounts.utils import send_verification_email
from config.settings import TOKEN_EXPIRY

signer = TimestampSigner()


@extend_schema(**signup_schema)
@api_view(["POST"])
def signup(request: Request) -> Response:
    """
    Registers a new user.

    This endpoint validates the provided sign-up data via SignUpSerializer,
    creates a new user with is_active set to False, and sends a
    verification email.

    Returns:

        - HTTP 201 with a confirmation token upon successful registration.
        - HTTP 400 if validation fails or the email verification cannot be
            sent.
    """
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        user: User = serializer.save()
        user.is_active = False
        user.save()
        try:
            send_verification_email(request, user)
        except Exception as e:
            user.delete()
            return Response(
                {
                    "message": f"failed to send verification email: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        message = {
            "message": "User created successfully",
        }
        return Response(message, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**confirm_email_schema)
@api_view(["GET"])
def confirm_email(request: Request, token: str) -> Response:
    """
    Confirms a user's email using a provided token.

    The token is unsinged to retrieve the user ID. If valid and the user is not
    yet active, the account is activated.

    Args:
        token (str): The email verification token.

    Returns:

        - HTTP 200 if the email is verified successfully.
        - HTTP 400 if the token is invalid/expired or the email is
            already verified.
        - HTTP 404 if no matching user is found.
    """
    try:
        user_id: str = signer.unsign(token, max_age=TOKEN_EXPIRY)
        user: User = get_object_or_404(User, pk=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()
            return Response(
                {"message": "Email verified successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Email is already verified."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except SignatureExpired:
        return Response(
            {"message": "Token has expired. Request a new one."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except BadSignature:
        return Response(
            {"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
        )
    except User.DoesNotExist:
        return Response(
            {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(**resend_verification_email_schema)
@api_view(["GET"])
def resend_verification_mail(request: Request) -> Response:
    """
    Resends the verification email to the user.

    This endpoint retrieves the user's email from the query parameters,
    verifies that the user exists and is not yet active, then sends a new
    verification email.

    Returns:

        - HTTP 200 with a new confirmation token if successful.
        - HTTP 400 if no email is provided or the email is already verified.
        - HTTP 404 if the user is not found.
    """
    email: str | None = request.query_params.get("email")
    if not email:
        return Response(
            {"message": "No email is provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user: User = User.objects.get(email=email)
        if user.is_active:
            return Response(
                {"message": "Email is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        send_verification_email(request, user)
        return Response(
            {
                "message": "Verification email sent",
            },
            status=status.HTTP_200_OK,
        )

    except User.DoesNotExist:
        return Response(
            {"message": "User not found"}, status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(**login_schema)
@api_view(["POST"])
def login(request):
    """
    Authenticate a user and generate access and refresh tokens.

    This endpoint validates the provided credentials using LoginSerializer.
    On successful authentication, it returns a JWT access token and refresh
    token.

    Returns:

        - HTTP 200 with JWT tokens upon successful login.
        - HTTP 401 if authentication fails.
        - HTTP 400 if validation errors occur.
    """
    serializer = LoginSerializer(data=request.data)
    try:
        if serializer.is_valid():
            user = serializer.validated_data
            message: Dict[str, str] = serializer.get_tokens(user)
            message["message"] = "Login successful"
            return Response(message, status=status.HTTP_200_OK)
    except AuthenticationFailed as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_401_UNAUTHORIZED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**refresh_token_schema)
@api_view(["POST"])
def refresh_token(request):
    """
    Refresh JWT access token.

    This endpoint allows users to exchange a valid refresh
    token for a new access token.

    Returns:
        - HTTP 200 with a new access token.
        - HTTP 400 if the refresh token is invalid.
    """
    serializer = RefreshTokenSerializer(data=request.data)

    if serializer.is_valid():
        refresh_token = serializer.validated_data["refresh"]  # type: ignore

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response(
                {"access": access_token}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"message": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema()
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    Protected endpoint that requires authentication.

    Returns:
        - HTTP 200 if authentication is successful.
        - HTTP 401 if the token is missing or invalid.
    """
    return Response(
        {"message": "You have accessed a protected route!"},
        status=status.HTTP_200_OK,
    )
