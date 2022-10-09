from django.urls import path
from . import views

app_name = "api-v1"

urlpatterns = [
    path("users", views.UserListView.as_view()),
    path("users/<int:pk>", views.UserManageView.as_view()),
    path("games", views.GameListView.as_view()),
    path("games/<int:pk>", views.GameDetailView.as_view(), name="game-detail"),
    path("games/<int:game_pk>/goals", views.GameGoalListView.as_view()),
    path("games/<int:game_pk>/goals/<int:goal_pk>", views.GameGoalManageView.as_view()),
    path("games/<int:game_pk>/teams/<int:team_pk>", views.AddGameMemberView.as_view()),
]
