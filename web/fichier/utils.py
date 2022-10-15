# -*- coding: UTF-8 -*-

from calendar import LocaleHTMLCalendar
from datetime import datetime as dtime, date, time, timedelta
import datetime
import locale
from django.db.models import Func, F, Value
from django.db import models
from django.urls import reverse
from django.utils import timezone

import html.entities

table = {k: '&{};'.format(v) for k, v in html.entities.codepoint2name.items()}

message_glossaire = "Encadrer un terme par des crochets pour qu'il devienne un lien vers l'entrée de glossaire correspondante (exemple: [aidant])."
message_sortable = "L'ordre des éléments peut être changé glisser/déposer"


def arrayToString(field: str):
    return Func(
        F(field),
        Value(", "),
        Value(""),
        function="array_to_string",
        output_field=models.TextField(),
    )


class Agenda(LocaleHTMLCalendar):
    month_name = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    day_name = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

    def __init__(self, events=None, *args):
        super(Agenda, self).__init__(*args)
        self.events = events
        self.today = timezone.now()

    def year(self, year):
        return self.formatyear(year, 1)

    def month(self, year, month, simple, current):
        return self.formatmonth(year, month, simple=simple, current=current)

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """

        if withyear:
            return ('<tr><th colspan="7" class="%s">' % self.cssclass_month_head) + \
                str(Agenda.month_name[themonth]) + \
                ' <a href="' + reverse('fichier:agenda_year', kwargs={'year': theyear}) + '">%s</a>' % theyear + \
                '</th></tr>'
        else:
            return ('<tr><th colspan="7" class="%s">' % self.cssclass_month_head) + \
                '<a href="' + reverse('fichier:agenda_month', kwargs={'year': theyear, 'month': themonth}) + '">%s</a>' % Agenda.month_name[themonth] + \
                '</th></tr>'

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        day_abbr = ["Lun", "Ma", "Mer", "Je", "Ven", "Sam", "Di"]

        return '<th class="%s">%s</th>' % (
            self.cssclasses_weekday_head[day], day_abbr[day])

    def formatday(self, theyear, themonth, day, weekday, events, simple, current):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:
            events_from_day = events.filter(date__day=day)
            if events_from_day.count() != 0:
                event_html = '<a class="day existing-day'
                if self.today.year == theyear and self.today.month == themonth and self.today.day == day:
                    event_html += ' today'
                if current is not None and theyear == current.year and themonth == current.month and day == current.day:
                    event_html += ' current'
                event_html += '" href="' + events_from_day[0].get_absolute_url() + '">' + str(day)
                if not simple and events_from_day[0].marque:
                    event_html += " ☑"
                event_html += "</a>"
            else:
                event_html = '<a class="day missing-day" href="/fichier/agenda/add/?date=' + \
                    str(day) + '/' + "{0:02d}".format(themonth) + '/' + str(theyear) + \
                    '">' + str(day) + "</a>"

            return '<td class="%s">%s</td>' % (self.cssclasses[weekday], event_html)

    def formatweek(self, theyear, themonth, theweek, events, simple, current):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(theyear, themonth, d, wd, events, simple, current) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True, simple=False, current=None):
        """
        Return a formatted month as a table.
        """
        if self.events is None:
            events = self.events.filter(date__year=theyear, date__month=themonth)
        else:
            events = self.events

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(theyear, themonth, week, events, simple, current))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


def to_iso(d):
    e = d.split("/")
    return e[2] + "-" + e[1] + "-" + e[0]
