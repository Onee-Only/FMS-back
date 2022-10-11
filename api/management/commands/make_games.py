import datetime
from django.core.management.base import BaseCommand
from api.models import Game, Team


class Command(BaseCommand):

    help = "this command creates games"

    def handle(self, *args, **options):
        now = datetime.datetime.now().date()
        if Game.objects.filter(date=now).count() == 0:
            lunch_game = Game.objects.create(
                weekday=now.isoweekday(),
                status=Game.Status.BEFORE,
                time=Game.Times.LUNCH,
            )
            create_team(lunch_game)
            if now.isoweekday() != 5:
                dinner_game = Game.objects.create(
                    weekday=now.isoweekday(),
                    status=Game.Status.BEFORE,
                    time=Game.Times.DINNER,
                )
                create_team(dinner_game)
            print(f"{now} : Games created.")
        else:
            print(f"{now} : Games already exist.")


def create_team(obj):
    team1 = Team.objects.create()
    obj.teams.add(team1)
    team2 = Team.objects.create()
    obj.teams.add(team2)
