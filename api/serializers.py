from django.http import Http404
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from . import models


class CustomRegisterSerializer(RegisterSerializer):
    username = serializers.CharField(
        max_length=5,
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED,
    )
    password2 = None
    grade = serializers.ChoiceField(choices=models.CustomUser.Grades.choices)

    def validate(self, data):
        return data

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "grade": self.validated_data.get("grade", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.grade = self.cleaned_data.get("grade")
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ("pk", "username", "grade", "goals", "assists")


class UserManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ("pk", "username", "is_staff", "grade", "goals", "assists")


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ("pk", "grade", "username")


class TeamSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True)
    goals = serializers.IntegerField(source="get_member_goals_count")

    class Meta:
        model = models.Team
        fields = ("members", "goals")


class GoalRetrieveSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField(read_only=True)
    goal_player = MemberSerializer()
    assist_player = MemberSerializer()

    class Meta:
        model = models.Goal
        fields = "__all__"

    def get_team(self, obj):
        for team in obj.game.teams.all():
            if obj.goal_player in team.members.all():
                return team.pk
        raise Http404()


class GoalManageSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Goal
        fields = "__all__"

    def get_team(self, obj):
        for team in obj.game.teams.all():
            if obj.goal_player in team.members.all():
                return team.pk
        raise Http404()

    def create(self, validated_data):
        obj = models.Goal.objects.create(**validated_data)
        obj.goals_assists_change(True)
        return obj

    def update(self, instance, validated_data):
        instance.goals_assists_change(False)
        instance = super().update(instance, validated_data)
        instance.goals_assists_change(True)
        return instance


class GameSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True)
    goals = GoalRetrieveSerializer(many=True)

    class Meta:
        model = models.Game
        fields = "__all__"
