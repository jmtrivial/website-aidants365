from fichier.models import EntetePage


def run():
    entetes = EntetePage.objects.filter(page="motscles")
    entetes.delete()
    for entete in entetes:
        print(entete.page)

