from django.urls import path

from . import views

urlpatterns = [
    path("signup", views.signup),
    path("login", views.login),
    path("confirm-email/<str:token>", views.confirm_email),
    path("resend_verification_mail", views.resend_verification_mail),
    path("protected", views.protected_view),
]
