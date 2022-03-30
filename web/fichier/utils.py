# -*- coding: UTF-8 -*-

from calendar import LocaleHTMLCalendar
from datetime import datetime as dtime, date, time
import datetime
from django.utils.translation import gettext as _
import locale


class Ephemeride:

    def __init__(self, d=None, url="", empty=True):
        self.date = d
        self.empty = empty
        self.url = url

    def day(self):
        return self.date.day

    def month(self):
        return self.date.month

    def year(self):
        return self.date.year

    def _ephemeride(self, url):
        return "<div class=\"ephemeride\"><a href=\"" + url + "\"> \
            <div class=\"jour_semaine\">" + _(self.date.strftime("%A")) + "</div> \
            <div class=\"jour\">" + str(self.date.day) + "</div> \
            <div class=\"mois\">" + _(self.date.strftime("%B")) + "</div> \
            </a></div>"

    def ephemeride(self):
        if self.empty:
            return self._ephemeride(url="/admin/fichier/entreeagenda/add/?date=" + str(self.day()) + '/' + str(self.month()) + '/' + str(self.year()))
        else:
            return self._ephemeride(url=self.url)


class Agenda(LocaleHTMLCalendar):
    def __init__(self, events=None, *args):
        super(Agenda, self).__init__(*args)
        self.events = events

    def annee_courante(self):
        return self.formatyear(2022, 1)

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        month_name = ["", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th colspan="7" class="%s">%s</th></tr>' % (
            self.cssclass_month_head, s)

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        day_abbr = ["Lun", "Ma", "Mer", "Je", "Ven", "Sam", "Di"]

        return '<th class="%s">%s</th>' % (
            self.cssclasses_weekday_head[day], day_abbr[day])

    def formatday(self, theyear, themonth, day, weekday, events):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        else:

            events_from_day = events.filter(date__day=day)
            if events_from_day.count() != 0:
                event_html = '<a class="day existing-day" href="' + events_from_day[0].get_absolute_url() + '">' + str(day) + "</a>"
            else:
                event_html = '<a class="day missing-day" href="/admin/fichier/entreeagenda/add/?date=' + \
                    str(day) + '/' + str(themonth) + '/' + str(theyear) + \
                    '">' + str(day) + "</a>"

            return '<td class="%s">%s</td>' % (self.cssclasses[weekday], event_html)

    def formatweek(self, theyear, themonth, theweek, events):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(theyear, themonth, d, wd, events) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """

        events = self.events.filter(date__year=theyear, date__month=themonth)

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(theyear, themonth, week, events))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
