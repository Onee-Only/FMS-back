from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS

from rest_framework import mixins
from rest_framework.generics import GenericAPIView


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
