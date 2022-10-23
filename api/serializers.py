from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from . import models, utils


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


class BaseUserSerializer(serializers.ModelSerializer):
    attack_point = serializers.IntegerField(source="get_attack_point")

    class Meta:
        model = models.CustomUser
        fields = (
            "id",
            "username",
            "grade",
            "goals",
            "assists",
            "attack_point",
            "rank",
        )
        abstract = True


class UserListSerializer(BaseUserSerializer):
    me = serializers.SerializerMethodField()

    class Meta:
        model = BaseUserSerializer.Meta.model
        fields = BaseUserSerializer.Meta.fields
        fields += ("me",)

    def get_me(self, obj):
        return obj.pk == self.context["request"].user.pk


class UserManageSerializer(BaseUserSerializer):
    class Meta:
        model = BaseUserSerializer.Meta.model
        fields = BaseUserSerializer.Meta.fields
        fields += ("is_staff",)


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomUser
        fields = ("id", "grade", "username")


class TeamSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True)
    goals = serializers.IntegerField(source="get_member_goals_count")

    class Meta:
        model = models.Team
        fields = ("members", "goals")


class GoalRetrieveSerializer(serializers.ModelSerializer):
    team = serializers.IntegerField(source="get_team")
    goal_player = MemberSerializer()
    assist_player = MemberSerializer()

    class Meta:
        model = models.Goal
        fields = "__all__"


class GoalManageSerializer(serializers.ModelSerializer):
    team = serializers.IntegerField(source="get_team")

    class Meta:
        model = models.Goal
        fields = "__all__"

    def create(self, validated_data):
        obj = models.Goal.objects.create(**validated_data)
        obj.goals_assists_change(True)
        utils.sort_rank()
        return obj

    def update(self, instance, validated_data):
        instance.goals_assists_change(False)
        instance = super().update(instance, validated_data)
        instance.goals_assists_change(True)
        utils.sort_rank()
        return instance


class GameSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True)
    goals = GoalRetrieveSerializer(many=True)

    class Meta:
        model = models.Game
        fields = "__all__"
