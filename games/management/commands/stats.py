import json
from datetime import datetime, timedelta
from collections import namedtuple

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import requests
import pytz

from games.models import Game, Release


Metric = namedtuple('Metric', 'users, games, releases, downloads, plays')


def growth_rate(current, previous):
    return (current - previous) / float(previous or 1) * 100


def breakdown(weeks):
    print "Date       Users    GR% Games    GR% Releases   GR% Plays    GR%"
    report = "{} {:5} {:5.0f}% {:5} {:5.0f}% {:7} {:5.0f}% {:5} {:5.0f}%"
    previous = None
    for week, m in weeks:
        if previous is None:
            print report.format(week.date(), m.users, 0, m.games, 0,
                                m.releases, 0, m.plays, 0)
        else:
            user_rate = growth_rate(m.users, previous.users)
            play_rate = growth_rate(m.plays, previous.plays)
            game_rate = growth_rate(m.games, previous.games)
            rele_rate = growth_rate(m.releases, previous.releases)
            print report.format(week.date(), m.users, user_rate,
                                m.games, game_rate, m.releases, rele_rate,
                                m.plays, play_rate)
        previous = m


def crunch_numbers(begin, end):
    gc = Game.objects.filter(created__lt=end, created__gte=begin).count()
    rc = Release.objects.filter(created__lt=end, created__gte=begin).count()
    uc = User.objects.filter(date_joined__lt=end,
                             date_joined__gte=begin).count()
    # TODO: Add download numbers

    # Add play numbers
    keen = "https://api.keen.io/3.0/projects/{}/queries/count"

    timeframe = {
        "start": begin.astimezone(pytz.UTC).isoformat(),
        "end": end.astimezone(pytz.UTC).isoformat(),
    }

    params = {
        "api_key": settings.KEEN_READ_KEY,
        "timeframe": json.dumps(timeframe),
        "event_collection": "opens",
    }

    resp = requests.get(keen.format(settings.KEEN_PROJECT_ID), params=params)
    resp.raise_for_status()

    return Metric(uc, gc, rc, 0, resp.json().get('result', 0))


class Command(BaseCommand):
    help = 'Show week-over-week growth rates'

    def handle(self, *args, **options):
        pacific = pytz.timezone('US/Pacific')
        week_begin = pacific.localize(datetime(2013, 12, 13))
        week_end = week_begin + timedelta(days=3)

        print "Week over week"
        print

        weeks = []

        while week_begin < datetime.now(pacific):
            weeks.append((week_begin, crunch_numbers(week_begin, week_end)))
            week_begin = week_end
            week_end = week_begin + timedelta(days=7)

        breakdown(weeks)

        print
        print "Month over month"
        print

        december = pacific.localize(datetime(2013, 12, 13))
        january = pacific.localize(datetime(2014, 1, 1))
        february = pacific.localize(datetime(2014, 2, 1))

        months = [
            (december, crunch_numbers(december, january)),
            (january, crunch_numbers(january, february)),
        ]

        breakdown(months)
