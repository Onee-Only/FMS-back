from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("user/", views.UserListView.as_view()),
    path("user/<int:pk>/", views.UserManageView.as_view()),
    path("game/", views.GameListView.as_view()),
    path("game/<int:pk>/", views.GameDetailView.as_view(), name="game-detail"),
    path("game/<int:game_pk>/team/<int:team_pk>/", views.AddGameMemberView.as_view()),
]
