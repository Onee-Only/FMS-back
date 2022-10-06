from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.pagination import PageNumberPagination


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


class GamePagenation(PageNumberPagination):
    page_size = 2
