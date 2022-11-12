from fichier.models import CategorieLibre, MotCle, Fiche


def run():
    # récupérer toutes les catégories libres
    clibres = CategorieLibre.objects.all()

    for c in clibres:
        obj, created = MotCle.objects.get_or_create(nom=c.nom)
        if created:
            print("création de l'étiquette " + c.nom)
        else:
            print("l'étiquette " + c.nom + " existe déjà")

        print("Mise à jour des fiches")
        for f in Fiche.objects.filter(categories_libres=c.id):
            f.mots_cles.add(obj.id)
            f.save()


