import requests
from django.http import Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    RegisterView,
    ConfirmEmailView,
)
from allauth.account.models import EmailAddress

from api import utils


class ResendEmailView(ResendEmailVerificationView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = EmailAddress.objects.filter(**serializer.validated_data).first()
        if email.email.split("@")[1] != "gsm.hs.kr":
            return Response(
                {"에러": "도메인이 gsm.hs.kr이어야 합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        if email:
            if email.verified:
                return Response(
                    {"에러": "이미 인증된 이메일입니다."}, status=status.HTTP_406_NOT_ACCEPTABLE
                )
            else:
                email.send_confirmation(request)

        return Response({"detail": "ok"}, status=status.HTTP_200_OK)


class SignupView(RegisterView):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        if email.split("@")[1] != "gsm.hs.kr":
            return Response(
                {"에러": "도메인이 gsm.hs.kr이어야 합니다."}, status=status.HTTP_403_FORBIDDEN
            )
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = self.get_response_data(user)
        utils.sort_rank()

        if data:
            response = Response(
                data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            response = Response(status=status.HTTP_204_NO_CONTENT, headers=headers)

        return response


class EmailConfirmView(ConfirmEmailView):
    def get(self, *args, **kwargs):
        self.object = self.get_object()
        try:
            email = EmailAddress.objects.get(email=self.object.email_address)
            if email.verified:
                return Response({"에러": "이미 인증되었습니다."}, status=status.HTTP_403_FORBIDDEN)
            return self.post(*args, **kwargs)
        except EmailAddress.DoesNotExist:
            raise Http404()


class ConfirmPasswordResetView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        uidb64 = kwargs["uidb64"]
        token = kwargs["token"]
        data = {
            "new_password1": "k4319812",
            "new_password2": "k4319812",
            "uid": uidb64,
            "token": token,
        }
        response = requests.post(
            "http://localhost:8000/auth/password/reset/confirm/",
            data=data,
        )

        return HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers["Content-Type"],
        )
