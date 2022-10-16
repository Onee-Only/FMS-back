from django.http import Http404
from django.shortcuts import redirect, reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
    GenericAPIView,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from dj_rest_auth.registration import app_settings
from dj_rest_auth.registration.views import (
    ResendEmailVerificationView,
    RegisterView,
    ConfirmEmailView,
)
from allauth.account.models import EmailAddress
from . import models, serializers, utils


class UserListView(ListAPIView):
    serializer_class = serializers.UserListSerializer

    def get_queryset(self):
        ordering = self.request.GET.get("ordering", None)
        if ordering is not None:
            if ordering == "goals":
                queryset = models.CustomUser.objects.order_by("-goals")
            elif ordering == "assists":
                queryset = models.CustomUser.objects.order_by("-assists")
        else:
            queryset = models.CustomUser.objects.all()
        return queryset


class UserManageView(RetrieveUpdateDestroyAPIView):
    permission_classes = [utils.IsStaffOrOwnerOrReadOnly]
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserManageSerializer

    def get_object(self):
        try:
            user = models.CustomUser.objects.get(id=self.kwargs["pk"])
            self.check_object_permissions(self.request, user)
            return user
        except models.CustomUser.DoesNotExist:
            raise Http404()

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if (
            serializer.validated_data.get("is_staff") is not None
            or serializer.validated_data.get("goals") is not None
            or serializer.validated_data.get("assists") is not None
        ):
            if not request.user.is_staff:
                raise PermissionDenied()
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class GameListView(ListAPIView):
    serializer_class = serializers.GameSerializer

    def get_queryset(self):
        weekday = self.request.GET.get("weekday", None)
        if weekday is not None:
            weekday = int(weekday)
            try:
                queryset = models.Game.objects.filter(weekday=weekday)
            except models.Game.DoesNotExist:
                raise Http404()
        else:
            queryset = models.Game.objects.all()
        return queryset


class GameDetailView(RetrieveUpdateAPIView):
    permission_classes = [utils.IsStaffOrOwnerOrReadOnly]
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    def put(self, request, *args, **kwargs):
        raise PermissionDenied()


class AddGameMemberView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = models.Game.objects.all()

    def get(self, request, *args, **kwargs):

        game = self.queryset.get(pk=kwargs["game_pk"])

        if game.status == models.Game.Status.BEFORE:
            try:
                qs = models.Team.objects.all()
                team = qs.get(pk=kwargs["team_pk"])

                if team.members.count() == 8:
                    return Response({"에러": "팀이 모두 찼습니다."})

                for game_team in qs.filter(game=game):
                    if request.user in game_team.members.all():
                        if game_team.pk != team.pk:
                            return Response({"에러": "이미 다른 팀에 소속돼 있습니다."})
                        team.members.remove(request.user)
                        return self.save_and_redirect(team, game)

                team.members.add(request.user)
                return self.save_and_redirect(team, game)

            except models.Team.DoesNotExist:
                raise Http404()
        else:
            return Response({"에러": "신청 시간이 지났습니다."})

    def save_and_redirect(self, team, game):
        team.save()
        return redirect(reverse("api-v1:game-detail", kwargs={"pk": game.pk}))


class GameGoalManageView(utils.UpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.GoalManageSerializer

    def get_object(self):
        return self.get_queryset()

    def get_queryset(self):
        try:
            queryset = models.Goal.objects.get(pk=self.kwargs.get("goal_pk"))
            return queryset
        except models.Game.DoesNotExist or models.Goal.DoesNotExist:
            raise Http404()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.goals_assists_change(False)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GameGoalListView(ListCreateAPIView):
    serializer_class = serializers.GoalRetrieveSerializer

    def get_object(self):
        return self.get_queryset()

    def get_queryset(self):
        try:
            game = models.Game.objects.get(pk=self.kwargs.get("game_pk"))
            goal = models.Goal.objects.filter(game=game)
            return goal
        except models.Game.DoesNotExist or models.Goal.DoesNotExist:
            raise Http404()

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()
        serializer = serializers.GoalManageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


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
        try:
            self.object = self.get_object()
            # if self.object.verified:
            #      return Response({"에러": "이미 인증되었습니다."}, status=status.HTTP_403_FORBIDDEN)
            if app_settings.CONFIRM_EMAIL_ON_GET:
                return self.post(*args, **kwargs)
        except Http404:
            self.object = None
        ctx = self.get_context_data()
        return self.render_to_response(ctx)
