from fichier.views import FichesViewPDF
from fichier.models import Fiche
from django.http import HttpRequest
import os
import datetime
import zoneinfo


def run():
    filename = '/media/fiches.pdf'
    exists = os.path.exists(filename)
    if exists:

        m_time = os.path.getmtime(filename)
        paris_tz = zoneinfo.ZoneInfo("Europe/Paris")
        dt_m = datetime.datetime.fromtimestamp(m_time).replace(tzinfo=paris_tz)

        date_derniere_modification = Fiche.objects.latest("date_derniere_modification").date_derniere_modification
        date_demande_mise_a_jour = Fiche.objects.latest("date_demande_mise_a_jour").date_demande_mise_a_jour

    if exists and dt_m > date_derniere_modification and dt_m > date_demande_mise_a_jour:
        print("Le fichier est assez récent")
    else:
        view = FichesViewPDF.as_view()
        request = HttpRequest()
        request.method = "GET"
        request.META["SERVER_NAME"] = "127.0.0.1"
        request.META["SERVER_PORT"] = "8080"

        print("Le fichier doit être mis à jour")
        result = view(request)

        with open(filename, 'wb') as file:
            file.write(result.rendered_content)
