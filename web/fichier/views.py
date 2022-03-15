from django.http import HttpResponse
from django.template import loader
from .models import Fiche, Niveau, Categorie, Auteur, CategorieLibre, Theme, MotCle
from django.shortcuts import get_object_or_404, render
from .forms import FicheForm
from django.db.models import Count, Q


def accueil(request):
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')[:5]

    niveaux = Niveau.objects.annotate(fiche_count=Count('fiche')).order_by("ordre")
    categories = Categorie.objects.annotate(fiche_count=Count('fiche_categorie1') + Count('fiche_categorie2') + Count('fiche_categorie3')).order_by("nom")
    auteurs = Auteur.objects.annotate(fiche_count=Count('fiche'))
    themes = Theme.objects.annotate(fiche_count=Count('fiche'))
    motcles = MotCle.objects.annotate(fiche_count=Count('fiche'))
    categories_libres = CategorieLibre.objects.annotate(fiche_count=Count('fiche'))

    context = {'fiche_list': latest_fiche_list, "nb_fiches": Fiche.objects.count(), "niveaux": niveaux,
               "categories": categories, "auteurs": auteurs, "themes": themes, "motcles": motcles, "categories_libres": categories_libres}
    return render(request, 'fiches/accueil.html', context)


def index(request):
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')
    context = {'fiche_list': latest_fiche_list}
    return render(request, 'fiches/index.html', context)


def index_detail(request, id):
    fiche = get_object_or_404(Fiche, pk=id)
    fiche_list = Fiche.objects.filter()
    return render(request, 'fiches/index_detail.html', {'fiche': fiche, 'fiche_list': fiche_list})


def detail(request, id):
    fiche = get_object_or_404(Fiche, pk=id)
    return render(request, 'fiches/detail.html', {'fiche': fiche})


def index_niveau(request, id):
    niveau = get_object_or_404(Niveau, pk=id)
    fiches = Fiche.objects.filter(niveau=niveau)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "niveau", "critere": niveau, "critere_human": "du niveau", "critere_nom": str(niveau), "fiche_list": fiches})


def index_niveau_detail(request, id1, id2):
    niveau = get_object_or_404(Niveau, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(niveau=niveau)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "niveau", "critere": niveau, "critere_human": "du niveau", "critere_nom": str(niveau), "fiche_list": fiches, "fiche": fiche})


def index_categorie(request, id):
    categorie = get_object_or_404(Categorie, pk=id)
    fiches = Fiche.objects.filter(Q(categorie1=categorie) | Q(categorie2=categorie) | Q(categorie3=categorie))
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "categorie", "critere": categorie, "critere_human": "du catégorie", "critere_nom": str(categorie), "fiche_list": fiches})


def index_categorie_detail(request, id1, id2):
    categorie = get_object_or_404(Categorie, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(Q(categorie1=categorie) | Q(categorie2=categorie) | Q(categorie3=categorie))
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "categorie", "critere": categorie, "critere_human": "de la catégorie", "critere_nom": str(categorie), "fiche_list": fiches, "fiche": fiche})


def index_auteur(request, id):
    auteur = get_object_or_404(Auteur, pk=id)
    fiches = Fiche.objects.filter(auteur=auteur)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "auteur", "critere": auteur, "critere_human": "de l'auteur", "critere_nom": auteur.nom, "fiche_list": fiches})


def index_auteur_detail(request, id1, id2):
    auteur = get_object_or_404(Auteur, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(auteur=auteur)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "auteur", "critere": auteur, "critere_human": "de l'auteur", "critere_nom": str(auteur), "fiche_list": fiches, "fiche": fiche})


def index_categorie_libre(request, id):
    categorie_libre = get_object_or_404(CategorieLibre, pk=id)
    fiches = Fiche.objects.filter(categories_libres=categorie_libre)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "categorie_libre", "critere": categorie_libre, "critere_human": "de la catégorie libre", "critere_nom": str(categorie_libre), "fiche_list": fiches})


def index_categorie_libre_detail(request, id1, id2):
    categorie_libre = get_object_or_404(CategorieLibre, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(categorie_libre=categorie_libre)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "categorie_libre", "critere": categorie_libre, "critere_human": "de la catégorie libre", "critere_nom": str(categorie_libre), "fiche_list": fiches, "fiche": fiche})


def index_theme(request, id):
    theme = get_object_or_404(Theme, pk=id)
    fiches = Fiche.objects.filter(themes=theme)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "theme", "critere": theme, "critere_human": "du thème", "critere_nom": str(theme), "fiche_list": fiches})


def index_theme_detail(request, id1, id2):
    theme = get_object_or_404(Theme, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(themes=theme)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "theme", "critere": theme, "critere_human": "du thème", "critere_nom": str(theme), "fiche_list": fiches, "fiche": fiche})


def index_motcle(request, id):
    motcle = get_object_or_404(MotCle, pk=id)
    fiches = Fiche.objects.filter(mots_cles=motcle)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "motcle", "critere": motcle, "critere_human": "du mot-clé", "critere_nom": str(motcle), "fiche_list": fiches})


def index_motcle_detail(request, id1, id2):
    motcle = get_object_or_404(MotCle, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(mots_cles=motcle)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "motcle", "critere": motcle, "critere_human": "du mot-clé", "critere_nom": str(motcle), "fiche_list": fiches, "fiche": fiche})

