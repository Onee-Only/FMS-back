from django.urls import path
from .views import core

app_name = "api-v1"

urlpatterns = [
    path("users", core.UserListView.as_view()),
    path("users/<int:pk>", core.UserManageView.as_view()),
    path("games", core.GameListView.as_view()),
    path("games/<int:pk>", core.GameDetailView.as_view(), name="game-detail"),
    path("games/<int:game_pk>/goals", core.GameGoalListView.as_view()),
    path("games/<int:game_pk>/goals/<int:goal_pk>", core.GameGoalManageView.as_view()),
    path("games/<int:game_pk>/teams/<int:team_pk>", core.AddGameMemberView.as_view()),
]
