"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from api.views.auth import (
    ResendEmailView,
    SignupView,
    EmailConfirmView,
    ConfirmPasswordResetView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("v1/", include("api.urls")),
    path("auth/", include("dj_rest_auth.urls")),
    path(
        "auth/password/reset/confirm/<str:uidb64>/<str:token>",
        ConfirmPasswordResetView.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/signup/", SignupView.as_view()),
    re_path(
        r"^auth/signup/account-confirm-email/(?P<key>[-:\w]+)/$",
        EmailConfirmView.as_view(),
        name="account_confirm_email",
    ),
    path("auth/signup/resend-email/", ResendEmailView.as_view()),
    path("auth/signup/", include("dj_rest_auth.registration.urls")),
]
