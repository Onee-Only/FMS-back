from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class CustomUser(AbstractUser):

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "grade"]

    class Grades(models.IntegerChoices):
        FIRST = 1, "1학년"
        SECOND = 2, "2학년"
        THIRD = 3, "3학년"

    username = models.CharField(
        max_length=5,
    )
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)
    grade = models.IntegerField(choices=Grades.choices)
    assists = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    goals = models.IntegerField(validators=[MinValueValidator(0)], default=0)


class Game(models.Model):
    class Status(models.TextChoices):
        BEFORE = "before", "경기 전"
        PLAYING = "playing", "경기 중"
        AFTER = "after", "경기 후"
        CANCELED = "canceled", "경기 취소"

    class Times(models.TextChoices):
        LUNCH = "lunch", "점심"
        DINNER = "dinner", "저녁"

    date = models.DateField(auto_now_add=True)
    status = models.CharField(choices=Status.choices, max_length=8)
    time = models.CharField(choices=Times.choices, max_length=6)
    teams = models.ManyToManyField("Team", related_name="game")


class Team(models.Model):
    members = models.ManyToManyField("CustomUser", related_name="+")

    def get_member_goals_count(self):
        game = self.game.all()[0]
        goals = Goal.objects.filter(game=game)
        sum = 0
        for member in self.members.all():
            for goal in goals:
                if member.pk == goal.goal_player.pk:
                    sum += 1
        return sum


class Goal(models.Model):

    game = models.ForeignKey("Game", related_name="goals", on_delete=models.CASCADE)
    time = models.TimeField()
    goal_player = models.ForeignKey(
        "CustomUser", related_name="+", on_delete=models.DO_NOTHING
    )
    assist_player = models.ForeignKey(
        "CustomUser", related_name="+", on_delete=models.DO_NOTHING
    )

    def goals_assists_change(self, is_creation):
        num = 1 if is_creation else -1
        self.goal_player.goals += num
        self.goal_player.save()
        self.assist_player.assists += num
        self.assist_player.save()
