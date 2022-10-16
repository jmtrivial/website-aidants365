from fichier.models import EntreeAgenda, EntreeGlossaire, Fiche, my_callback_pre_save, my_callback_pre_save_urls_agenda, my_callback_pre_save_urls_glossaire


def run():
    fiches = Fiche.objects.all()
    for fiche in fiches:
        my_callback_pre_save(None, fiche)
    Fiche.objects.bulk_update(fiches, fields=["urls"])
    entreesagenda = EntreeAgenda.objects.all()
    for e in entreesagenda:
        my_callback_pre_save_urls_agenda(None, e)
    EntreeAgenda.objects.bulk_update(entreesagenda, fields=["urls"])
    entreesglossaire = EntreeGlossaire.objects.all()
    for e in entreesglossaire:
        my_callback_pre_save_urls_glossaire(None, e)
    EntreeGlossaire.objects.bulk_update(entreesglossaire, fields=["urls"])
