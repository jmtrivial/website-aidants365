from fichier.views import FichesViewPDF
from django.http import HttpRequest


def run():
    view = FichesViewPDF.as_view()
    request = HttpRequest()
    request.method = "GET"
    request.META["SERVER_NAME"] = "127.0.0.1"
    request.META["SERVER_PORT"] = "8080"

    result = view(request)

    with open('/media/fiches.pdf', 'wb') as file:
        file.write(result.rendered_content)
