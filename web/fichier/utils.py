# -*- coding: UTF-8 -*-

from calendar import LocaleHTMLCalendar
from datetime import datetime as dtime, date, time
import datetime
from .models import EntreeCalendrier


class Calendrier(LocaleHTMLCalendar):
    def __init__(self, events=None, *args):
        super(Calendrier, self).__init__(*args)
        self.events = events

    def annee_courante(self):
        return self.formatyear(2022, 1)

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
                event_html = '<a class="day missing-day" href="/admin/fichier/entreecalendrier/add/?date=' + \
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