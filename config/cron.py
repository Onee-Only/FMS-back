import datetime
from django.db.models import Q
from api.models import Game, Team


def print_log(date, time, msg):
    print(f"[{date}] {time} : {msg}")


def create_games():

    now = datetime.datetime.now().date()

    if Game.objects.filter(date=now).count() == 0:

        lunch_game = Game.objects.create(
            weekday=now.isoweekday(),
            status=Game.Status.BEFORE,
            time=Game.Times.LUNCH,
        )
        create_team(lunch_game)
        print_log(now, Game.Times.LUNCH, "Game created")

        if now.isoweekday() != 5:
            dinner_game = Game.objects.create(
                weekday=now.isoweekday(),
                status=Game.Status.BEFORE,
                time=Game.Times.DINNER,
            )
            create_team(dinner_game)
            print_log(now, Game.Times.DINNER, "Game created")

    else:
        print_log("Error", ":(", "Game(s) already exist. Aborted")


def create_team(obj):

    team1 = Team.objects.create()
    obj.teams.add(team1)
    team2 = Team.objects.create()
    obj.teams.add(team2)


def delete_games():

    games = Game.objects.all()

    for game in games:
        for team in game.teams.all():
            team.delete()
        game.delete()

    print_log("Deletion", ";)", "Games deleted")


def change_status(game, status):

    game.status = status
    game.save()


def get_date_time():

    now = datetime.datetime.now()
    date = now.date()
    time = now.time()

    if time > datetime.time(hour=14):
        time = Game.Times.DINNER
        if date.isoweekday == 5:
            print_log(date, time, "Friday doesn't have dinner game. Aborted")
            return None
    else:
        time = Game.Times.LUNCH
    return date, time


def get_game(date, time):

    try:
        game = Game.objects.get(Q(date=date) & Q(time=time))
        return game
    except Game.DoesNotExist:
        print_log("Error", ":)", "Game does not exist. Aborted")
        return None


def status_to_playing():

    date, time = get_date_time()
    if date is None:
        return

    game = get_game(date, time)
    if game is None:
        return

    if game.status == Game.Status.BEFORE:

        for team in game.teams.all():
            members = team.members.count()
            if members < 8:
                change_status(game, Game.Status.CANCELED)
                print_log(date, time, "Game canceled due to lack of members")
                return

        change_status(game, Game.Status.PLAYING)
        print_log(date, time, f"Game status successfully changed to: {game.status}")
    else:
        print_log(date, time, "Game status is not before. Aborted")


def status_to_after():

    date, time = get_date_time()
    if date is None:
        return

    game = get_game(date, time)
    if game is None:
        return

    if game.status == Game.Status.PLAYING:
        change_status(game, Game.Status.AFTER)
        print_log(date, time, f"Game status successfully changed to: {game.status}")
    else:
        print_log(date, time, "Game status is not playing. Aborted")
