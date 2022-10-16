from django.contrib import admin
from . import models


@admin.register(models.CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "grade")


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):

    list_display = ("date", "weekday", "status", "time")


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):

    list_display = ("pk",)


@admin.register(models.Goal)
class GoalAdmin(admin.ModelAdmin):

    list_display = (
        "game",
        "time",
        "goal_player",
        "assist_player",
    )
