from fichier.views import AgendaMonthViewPDF
from fichier.models import EntreeAgenda
from django.http import HttpRequest
import os
import datetime
import zoneinfo
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models import Count

def run():
    entries = EntreeAgenda.objects.annotate(year=TruncYear('date')).annotate(month=TruncMonth('date')).values('year', 'month').annotate(count=Count('pk'))
    for e in entries:
        year = e["year"].year
        month = e["month"].month

        str_year = str(year)
        str_month = ("0" if month < 10 else "") + str(month)

        filename = '/media/agenda-' + str_year + "-" + str_month + '.pdf'
        exists = os.path.exists(filename)
        if exists:
            m_time = os.path.getmtime(filename)
            paris_tz = zoneinfo.ZoneInfo("Europe/Paris")
            dt_m = datetime.datetime.fromtimestamp(m_time).replace(tzinfo=paris_tz)

            e_agenda = EntreeAgenda.objects.filter(date__year=year, date__month=month)
            date_derniere_modification = e_agenda.latest("date_derniere_modification").date_derniere_modification
            date_demande_mise_a_jour = e_agenda.latest("date_demande_mise_a_jour").date_demande_mise_a_jour

        if exists and dt_m > date_derniere_modification and dt_m > date_demande_mise_a_jour:
            print("L'agenda " + filename + " est assez récent")
        else:
            view = AgendaMonthViewPDF.as_view()
            request = HttpRequest()
            request.method = "GET"
            request.META["SERVER_NAME"] = "127.0.0.1"
            request.META["SERVER_PORT"] = "8080"

            print("L'agenda " + filename + " doit être mis à jour")
            result = view(request, year=year, month=month)

            with open(filename, 'wb') as file:
                file.write(result.rendered_content)
