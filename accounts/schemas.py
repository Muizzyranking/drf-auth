from drf_spectacular.utils import OpenApiParameter, OpenApiResponse
from accounts.serializers import (
    ErrorResponseSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    SignUpSerializer,
)

signup_schema = {
    "auth": None,
    "request": SignUpSerializer,
    "responses": {
        201: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "User created successfully",
                    },
                },
            },
            description="User created successfully.",
        ),
        400: ErrorResponseSerializer,
    },
}
confirm_email_schema = {
    "auth": None,
    "parameters": [
        OpenApiParameter(
            name="token",
            type=str,
            location=OpenApiParameter.PATH,
            required=True,
            description="Email verification token",
        )
    ],
    "responses": {
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Email verified successfully",
                    },
                },
            },
            description="Email verified successfully.",
        ),
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
}

resend_verification_email_schema = {
    **confirm_email_schema,
    "parameters": [
        OpenApiParameter(
            name="email",
            type=str,
            location=OpenApiParameter.QUERY,  # Changed to QUERY
            required=True,
            description="Email",
        )
    ],
}

login_schema = {
    "request": LoginSerializer,
    "auth": None,
    "responses": {
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Login successful",
                    },
                    "access": {
                        "type": "string",
                        "example": "eyJhbGciOiJIUzI1NiIs...",
                    },
                    "refresh": {
                        "type": "string",
                        "example": "eyJhbGciOiJIUzI1NiIs...",
                    },
                },
            },
            description=(
                "Returns access and refresh tokens on successful login."
            ),
        ),
        400: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Invalid email or password",
                    },
                },
            },
            description="Validation failed.",
        ),
        401: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": (
                            "Email not verified. Please verify your email."
                        ),
                    },
                },
            },
            description="Authentication failed.",
        ),
    },
}

refresh_token_schema = {
    "request": RefreshTokenSerializer,
    "responses": {
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "access": {
                        "type": "string",
                        "example": "eyJhbGciOiJIUzI1NiIs...",
                    }
                },
            },
            description="Returns a new access token.",
        ),
        400: OpenApiResponse(
            response={
                "type": "object",
                "properties": {"message": {"type": "string"}},
            },
            description="Invalid refresh token.",
        ),
    },
}
