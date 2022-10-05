from django.urls import path
from . import views

urlpatterns = [
    path("user/", views.UserListView.as_view()),
    path("user/<int:pk>/", views.UserManageView.as_view()),
]
