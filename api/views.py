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
from . import models, serializers, utils


class UserListView(ListAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserListSerializer


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
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class GameListView(ListAPIView):
    queryset = models.Game.objects.order_by("-id")
    serializer_class = serializers.GameSerializer
    pagination_class = utils.GamePagenation


class GameDetailView(RetrieveUpdateAPIView):
    permission_classes = [utils.IsStaffOrOwnerOrReadOnly]
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer


class AddGameMemberView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = models.Game.objects.all()

    def get(self, request, *args, **kwargs):
        game = self.queryset.get(pk=kwargs["game_pk"])
        if game.status == models.Game.Status.BEFORE:
            try:
                qs = models.Team.objects.all()
                team = qs.get(pk=kwargs["team_pk"])

                if team.members.count() == 11:
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
        return redirect(reverse("api:game-detail", kwargs={"pk": game.pk}))


class GameGoalManageView(utils.UpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = serializers.GoalSerializer

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
    serializer_class = serializers.GoalSerializer

    def get_object(self):
        return self.get_queryset()

    def get_queryset(self):
        try:
            game = models.Game.objects.get(pk=self.kwargs.get("game_pk"))
            goal = models.Goal.objects.filter(game=game)
            return goal
        except models.Game.DoesNotExist or models.Goal.DoesNotExist:
            raise Http404()
