from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import User


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Email already exists",
            )
        ],
        error_messages={"invalid": "Enter a valid email address."},
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = User.objects.filter(email=email).first()

            if not user or not user.check_password(password):
                raise AuthenticationFailed("Invalid email or password.")

            if not user.is_active:
                raise AuthenticationFailed(
                    "Email not verified. Please verify your email."
                )

            return user

        raise AuthenticationFailed("Invalid email or password")

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class ErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Error message description")
