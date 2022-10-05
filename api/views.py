from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from . import models, serializers, utils


class UserListView(ListAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserListSerializer


class UserManageView(RetrieveUpdateDestroyAPIView):
    permission_classes = [utils.IsStaffOrOwnerOrReadOnly]
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserManageSerializer
