from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework import mixins
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.generics import GenericAPIView
from api.models import CustomUser


class UpdateDestroyAPIView(
    GenericAPIView,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class IsStaffOrOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        if request.user.is_authenticated:
            if request.user.is_staff:
                return True

            if obj.__class__ == get_user_model():
                return obj.id == request.user.id

            if hasattr(obj, "goal_player"):
                return (
                    obj.goal_player.id == request.user.id
                    or obj.assist_player.id == request.user.id
                )

        return False


def sort_rank():

    players = CustomUser.objects.annotate(
        attack_point=F("assists") + F("goals")
    ).order_by("-attack_point")
    players_list = list(players)

    rank = 0
    attack_point = 0
    first_player = players.first()
    for player in players_list:
        if player != first_player:
            if player.get_attack_point() == attack_point:
                rank -= 1
        attack_point = player.get_attack_point()
        rank += 1
        player.rank = rank

    CustomUser.objects.bulk_update(players, ["rank"])
