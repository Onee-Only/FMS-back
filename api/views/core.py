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
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .. import models, serializers, utils


class UserListView(ListAPIView):
    serializer_class = serializers.UserListSerializer
    queryset = models.CustomUser.objects.order_by("rank")


@api_view(["GET"])
def get_me(request):

    if request.user.is_authenticated:
        user = models.CustomUser.objects.get(pk=request.user.pk)
        serializer = serializers.UserManageSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(data={"오류": "익명 유저입니다."}, status=status.HTTP_401_UNAUTHORIZED)


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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        utils.sort_rank()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        utils.sort_rank()
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
