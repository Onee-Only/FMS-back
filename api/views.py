from django.http import Http404
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
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
                raise Http404()
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class GameListView(ListAPIView):
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer


class GameDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer
