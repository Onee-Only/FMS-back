from django.core.management.base import BaseCommand
from api.models import Game


class Command(BaseCommand):

    help = "this command deletes games"

    def handle(self, *args, **options):
        games = Game.objects.all()
        for game in games:
            for team in game.teams:
                team.delete()
            game.delete()
        print("Games deleted")
