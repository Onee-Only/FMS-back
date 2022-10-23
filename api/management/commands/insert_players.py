import datetime
from django.core.management.base import BaseCommand
from api.models import Game, Team, CustomUser


class Command(BaseCommand):

    help = "this command creates games"

    def add_arguments(self, parser):
        parser.add_argument(
            "--time",
            default="lunch",
            type=str,
        )

    def handle(self, *args, **options):
        weekday = datetime.datetime.now().date().isoweekday()
        time = options.get("time")
        if time != "lunch" and time != "dinner":
            print("argument is wrong")
            return
        game = Game.objects.filter(weekday=weekday).get(time=time)
        teams = Team.objects.filter(game=game)
        team1, team2 = teams
        count = 0
        for user in CustomUser.objects.all():
            count += 1
            if count > 8:
                team2.members.add(user)
            else:
                if count > 16:
                    break
                team1.members.add(user)
