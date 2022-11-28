from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.template import loader
from .models import Fiche, Niveau, Categorie, Auteur, Theme, Etiquette, EntreeGlossaire, EntreeAgenda, Document, EntetePage, Ephemeride
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q, Case, When, IntegerField, Max, F, ExpressionWrapper, Value, FloatField, Subquery
from decimal import Decimal
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.http import Http404, HttpResponseRedirect
from .forms import FicheForm, EntreeGlossaireForm, EntreeAgendaForm, CategorieForm, ThemeForm, EtiquetteForm, ThemeMergeForm, EtiquetteMergeForm, NiveauForm, DocumentForm, EntetePageForm, EntreeAgendaInvertForm, EntreeAgendaInvertWithForm
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.generic.edit import DeleteView
import json
from datetime import datetime, date
from django.db import IntegrityError
from .utils import message_glossaire, message_sortable, to_iso
from django.db.models.functions import Ceil, Cast, Lower
from django.core.paginator import Paginator
from itertools import chain
from django.utils.safestring import mark_safe
from django.conf import settings

from django.views.generic import DetailView, ListView

from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import WeasyTemplateResponse
from weasyprint import HTML

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import Agenda, table, arrayToString

import logging
logger = logging.getLogger(__name__)


def get_entete(page):
    entetes = EntetePage.objects.filter(page=page)
    if entetes.count() == 0:
        return page
    else:
        return entetes[0]


def annoter_class_nuage(objects):
    nb_max = 5
    nb = objects.aggregate(Max("fiche_count"))["fiche_count__max"]
    logger.warning("count max " + str(nb))
    return objects.annotate(classe_nuage=Cast(Ceil(Cast(Value(nb_max) * F('fiche_count'), FloatField()) / Value(nb)), IntegerField())). \
        annotate(max_classe_nuage=Value(nb_max))


@login_required
def a_propos(request):
    aujourdhui = timezone.now()
    aujourdhui = Agenda.day_name[aujourdhui.weekday()] + " " + str(aujourdhui.day) + " " + Agenda.month_name[aujourdhui.month] + " " + str(aujourdhui.year)
    auteurs = Auteur.objects.annotate(fiche_count=Count('fiche'))

    context = {"nbfichestotal": Fiche.objects.count(),
               "auteurs": auteurs,
               "aujourdhui": aujourdhui,
               "nbentreesglossairetotal": EntreeGlossaire.objects.count(),
               'entete': get_entete("a_propos")}
    return render(request, 'fiches/a_propos.html', context)


@login_required
def accueil(request):
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')[:5]
    latest_entrees_glossaire_list = EntreeGlossaire.objects.order_by('-date_derniere_modification')[:5]
    latest_entrees_agenda_list = EntreeAgenda.objects.order_by('-date_derniere_modification')[:5]

    niveaux = Niveau.objects.annotate(fiche_count=Count('fiche')).order_by("ordre")

    themes = Theme.objects.annotate(fiche_count=Count('fiche', distinct=True) + Count('entreeagenda', distinct=True)).order_by("nom__unaccent")
    themes = annoter_class_nuage(themes)

    etiquettes = Etiquette.objects.annotate(fiche_count=Count('fiche', distinct=True) + Count('entreeagenda', distinct=True)).order_by("nom__unaccent")
    etiquettes = annoter_class_nuage(etiquettes)

    aujourdhui = timezone.now()
    entrees_agenda = EntreeAgenda.objects.filter(date=aujourdhui)
    if entrees_agenda.count() == 0:
        ephemeride = Ephemeride(timezone.now())
        entree_agenda = None
    else:
        entree_agenda = entrees_agenda[0]
        ephemeride = Ephemeride(entree_agenda)

    context = {'fiche_list': latest_fiche_list,
               'entrees_glossaire_list': latest_entrees_glossaire_list,
               'entrees_agenda_list': latest_entrees_agenda_list,
               "niveaux": niveaux,
               "themes": themes,
               "etiquettes": etiquettes,
               "entree_agenda": entree_agenda, "ephemeride": ephemeride, 'entete': get_entete("accueil"),
               "entete_mois": get_entete("agenda/" + str(aujourdhui.year) + "/" + ("0" + str(aujourdhui.month))[-2:] + "/"),
               "entete_mois_annee": aujourdhui.year, "entete_mois_mois": Agenda.month_name[aujourdhui.month]}
    return render(request, 'fiches/accueil.html', context)


@login_required
def index(request):
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')
    categories = annotate_categories_par_niveau().order_by("code__unaccent")
    categories = annoter_class_nuage(categories)
    context = {'fiche_list': latest_fiche_list, 'entete': get_entete("index"), "elements": categories, "critere_name_pluriel": "categories", "critere_name": "categorie"}
    return render(request, 'fiches/index.html', context)


@login_required
def index_detail(request, id):
    fiche = get_object_or_404(Fiche, pk=id)
    fiche_list = Fiche.objects.filter()
    return render(request, 'fiches/index_detail.html', {'fiche': fiche, 'fiche_list': fiche_list})


@login_required
def detail(request, id):
    fiche = get_object_or_404(Fiche, pk=id)
    search = request.GET.get('search')
    return render(request, 'fiches/detail.html', {'fiche': fiche, 'search': search})


@login_required
def agenda_sans_niveau(request):
    entrees = EntreeAgenda.objects.filter(niveau=None).order_by("date")
    return render(request, 'fiches/agenda_sans_niveau.html', {'entrees': entrees})


@login_required
def index_niveau(request, id):
    niveau = get_object_or_404(Niveau, pk=id)
    fiches = Fiche.objects.filter(niveau=niveau)
    entreesagenda = EntreeAgenda.objects.filter(niveau=niveau)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "niveau", "critere": niveau,
                                                             "critere_human": "du niveau", "critere_nom": str(niveau),
                                                             "fiche_list": fiches, "entrees_agenda_list": entreesagenda})


@login_required
def index_niveau_detail(request, id1, id2):
    niveau = get_object_or_404(Niveau, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(niveau=niveau)
    entreesagenda = EntreeAgenda.objects.filter(niveau=niveau)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "niveau", "critere": niveau,
                                                                    "critere_human": "du niveau", "critere_nom": str(niveau),
                                                                    "fiche_list": fiches, "entrees_agenda_list": entreesagenda, "fiche": fiche})


@login_required
def index_categorie(request, id):
    categorie = get_object_or_404(Categorie, pk=id)
    fiches = Fiche.objects.filter(Q(categorie1=categorie) | Q(categorie2=categorie) | Q(categorie3=categorie))
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "categorie", "critere": categorie,
                                                             "critere_human": "de la catégorie", "critere_nom": str(categorie),
                                                             "fiche_list": fiches})


@login_required
def index_categorie_detail(request, id1, id2):
    categorie = get_object_or_404(Categorie, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(Q(categorie1=categorie) | Q(categorie2=categorie) | Q(categorie3=categorie))
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "categorie", "critere": categorie,
                                                                    "critere_human": "de la catégorie", "critere_nom": str(categorie),
                                                                    "fiche_list": fiches, "fiche": fiche})


def annotate_categories_par_niveau():
    return Categorie.objects.filter(). \
        annotate(fiche_count1=Count("fiche_categorie1", distinct=True)). \
        annotate(fiche_count2=Count("fiche_categorie2", distinct=True)). \
        annotate(fiche_count3=Count("fiche_categorie3", distinct=True)). \
        annotate(fiche_count=F("fiche_count1") + F("fiche_count2") + F("fiche_count3")). \
        annotate(entry_count=F("fiche_count"))


def annotate_categories_par_niveau_complet():
    return annotate_categories_par_niveau(). \
        annotate(fiche_count_A1=Count("fiche_categorie1", filter=Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.A), distinct=True)). \
        annotate(fiche_count_A2=Count("fiche_categorie2", filter=Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.A), distinct=True)). \
        annotate(fiche_count_A3=Count("fiche_categorie3", filter=Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.A), distinct=True)). \
        annotate(fiche_count_B1=Count("fiche_categorie1", filter=Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.B), distinct=True)). \
        annotate(fiche_count_B2=Count("fiche_categorie2", filter=Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.B), distinct=True)). \
        annotate(fiche_count_B3=Count("fiche_categorie3", filter=Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.B), distinct=True)). \
        annotate(fiche_count_C1=Count("fiche_categorie1", filter=Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.C), distinct=True)). \
        annotate(fiche_count_C2=Count("fiche_categorie2", filter=Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.C), distinct=True)). \
        annotate(fiche_count_C3=Count("fiche_categorie3", filter=Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.C), distinct=True)). \
        annotate(fiche_count_A=F("fiche_count_A1") + F("fiche_count_A2") + F("fiche_count_A3")). \
        annotate(fiche_count_B=F("fiche_count_B1") + F("fiche_count_B2") + F("fiche_count_B3")). \
        annotate(fiche_count_C=F("fiche_count_C1") + F("fiche_count_C2") + F("fiche_count_C3"))


@login_required
def categories(request):
    categories = annotate_categories_par_niveau_complet().order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                   "elements": categories, "titre": "Toutes les catégories",
                                                   "nom_humain": "catégorie", "nom_humain_pluriel": "catégories",
                                                   "visu_code": "basic", "visu": "triées par nombre total de fiches",
                                                   'entete': get_entete("categories")})


@login_required
def categories_alpha(request):
    categories = annotate_categories_par_niveau_complet().order_by("-fiche_count").order_by(Lower("code__unaccent"))
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                   "elements": categories, "titre": "Toutes les catégories",
                                                   "nom_humain": "catégorie", "nom_humain_pluriel": "catégories",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique",
                                                   'entete': get_entete("categories")})


@login_required
def categories_nuage(request):
    categories = annotate_categories_par_niveau().order_by("code__unaccent")
    categories = annoter_class_nuage(categories)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                         "elements": categories, "titre": "Toutes les catégories",
                                                         "nom_humain": "catégorie", "nom_humain_pluriel": "catégories",
                                                         'entete': get_entete("categories")})


@login_required
def index_auteur(request, id):
    auteur = get_object_or_404(Auteur, pk=id)
    fiches = Fiche.objects.filter(auteur=auteur)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "auteur", "critere": auteur,
                                                             "critere_human": "de l'auteur", "critere_nom": auteur.nom,
                                                             "fiche_list": fiches})


@login_required
def index_auteur_detail(request, id1, id2):
    auteur = get_object_or_404(Auteur, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(auteur=auteur)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "auteur", "critere": auteur,
                                                                    "critere_human": "de l'auteur", "critere_nom": auteur.nom,
                                                                    "fiche_list": fiches, "fiche": fiche})


def annotate_categories_par_niveau_simple(objects, agenda=False):
    result = objects.annotate(fiche_count=Count('fiche', distinct=True)). \
        annotate(fiche_count_A=Count('fiche', filter=Q(fiche__niveau__applicable=Niveau.Applicabilite.A), distinct=True)). \
        annotate(fiche_count_B=Count('fiche', filter=Q(fiche__niveau__applicable=Niveau.Applicabilite.B), distinct=True)). \
        annotate(fiche_count_C=Count('fiche', filter=Q(fiche__niveau__applicable=Niveau.Applicabilite.C), distinct=True))
    if agenda:
        result = result.annotate(agenda_count=Count('entreeagenda', distinct=True)).annotate(entry_count=F("agenda_count") + F("fiche_count"))
    else:
        result = result.annotate(entry_count=F("fiche_count"))
    return result


@login_required
def index_theme(request, id):
    theme = get_object_or_404(Theme, pk=id)
    fiches = Fiche.objects.filter(themes=theme)
    agendas = EntreeAgenda.objects.filter(themes=theme).order_by("date")
    themes_connexes = Theme.objects.filter(id__in=Fiche.objects.filter(id__in=fiches.values("id")).values("themes")
                                           .union(Fiche.objects.filter(id__in=fiches.values("id")).values("themes"))
                                           ).exclude(id=id)

    return render(request, 'fiches/index_par_critere.html', {"critere_name": "theme", "critere": theme,
                                                             "critere_human": "du thème",
                                                             "critere_nom": str(theme), "fiche_list": fiches,
                                                             "themesconnexes": themes_connexes,
                                                             "entreesagenda": agendas})


@login_required
def index_theme_detail(request, id1, id2):
    theme = get_object_or_404(Theme, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(themes=theme)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "theme", "critere": theme,
                                                                    "critere_human": "du thème", "critere_nom": str(theme),
                                                                    "fiche_list": fiches, "fiche": fiche})


@login_required
def themes(request):
    themes = annotate_categories_par_niveau_simple(Theme.objects, True).order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les thèmes",
                                                   "nom_humain": "thème", "nom_humain_pluriel": "thèmes",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches",
                                                   'entete': get_entete("themes")})


@login_required
def themes_alpha(request):
    themes = annotate_categories_par_niveau_simple(Theme.objects, True).order_by("nom__unaccent")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les thèmes",
                                                   "nom_humain": "thème", "nom_humain_pluriel": "thèmes",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique",
                                                   'entete': get_entete("themes")})


@login_required
def themes_nuage(request):
    themes = Theme.objects.filter().annotate(fiche_count=Count('fiche', distinct=True) + Count('entreeagenda', distinct=True)). \
        order_by("nom__unaccent")
    themes = annoter_class_nuage(themes)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                         "elements": themes, "titre": "Tous les thèmes",
                                                         "nom_humain": "thème", "nom_humain_pluriel": "thèmes",
                                                         'entete': get_entete("themes")})


@login_required
def index_etiquette(request, id):
    etiquette = get_object_or_404(Etiquette, pk=id)
    fiches = Fiche.objects.filter(etiquettes=etiquette)
    agendas = EntreeAgenda.objects.filter(etiquettes=etiquette).order_by("date")
    glossaires = EntreeGlossaire.objects.filter(Q(entree=etiquette.nom) | Q(formes_alternatives__contains=[etiquette.nom]))
    etiquettes_connexes = Etiquette.objects.filter(id__in=EntreeAgenda.objects.filter(id__in=agendas.values("id")).values("etiquettes")
                                                   .union(Fiche.objects.filter(id__in=fiches.values("id")).values("etiquettes"))
                                                   ).exclude(id=id).order_by(Lower("nom__unaccent"))

    return render(request, 'fiches/index_par_critere.html', {"critere_name": "etiquette", "critere": etiquette,
                                                             "critere_human": "de l'étiquette", "critere_nom": str(etiquette),
                                                             "fiche_list": fiches, "entreesagenda": agendas,
                                                             "entreesglossaire": glossaires,
                                                             "etiquettesconnexes": etiquettes_connexes,
                                                             'entete': get_entete("themes")})


@login_required
def index_etiquette_detail(request, id1, id2):
    etiquette = get_object_or_404(Etiquette, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(etiquettes=etiquette)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "etiquette", "critere": etiquette,
                                                                    "critere_human": "de l'étiquette", "critere_nom": str(etiquette),
                                                                    "fiche_list": fiches, "fiche": fiche})


@login_required
def etiquettes(request):
    return etiquettes_page(request, 1)


@login_required
def etiquettes_page(request, key):
    etiquettes = annotate_categories_par_niveau_simple(Etiquette.objects, True).order_by("-fiche_count")
    step = 20
    mc = Paginator(etiquettes, step)
    nb_etiquettes = Etiquette.objects.count()
    extension_titre = "de " + str(step * (key - 1) + 1) + " à " + str(step * key)
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "etiquettes", "critere_name": "etiquette",
                                                   "elements": mc.page(key).object_list,
                                                   "nb_elements": nb_etiquettes,
                                                   "extension_titre": extension_titre,
                                                   "p_id": key,
                                                   "url_key_paginator": "fichier:etiquettes_page",
                                                   "paginator": mc,
                                                   "titre": "Étiquettes",
                                                   "nom_humain": "étiquette", "nom_humain_pluriel": "étiquettes",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches",
                                                   'entete': get_entete("etiquettes")})


@login_required
def etiquettes_alpha(request):
    return etiquettes_alpha_page(request, "A")


@login_required
def etiquettes_alpha_page(request, key):
    if key >= "A" and key <= "Z":
        etiquettes = annotate_categories_par_niveau_simple(Etiquette.objects, True).order_by(Lower("nom__unaccent")).filter(nom__istartswith=key)
        extension_titre = "commençant par " + key
    else:
        etiquettes = annotate_categories_par_niveau_simple(Etiquette.objects, True).order_by(Lower("nom__unaccent")).exclude(nom__unaccent__iregex=r'^[a-zA-Z].*$')
        extension_titre = "ne commençant pas par une lettre"
    nb_etiquettes = Etiquette.objects.count()
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "etiquettes", "critere_name": "etiquette",
                                                   "nb_elements": nb_etiquettes, "key_alpha": key,
                                                   "extension_titre": extension_titre,
                                                   "url_key_alpha": "fichier:etiquettes_alpha_page",
                                                   "elements": etiquettes, "titre": "Étiquettes",
                                                   "nom_humain": "étiquette", "nom_humain_pluriel": "étiquettes",
                                                   "visu_code": "alpha", "visu": "",
                                                   "entete": get_entete("etiquettes")})


@login_required
def etiquettes_nuage(request):
    etiquettes = Etiquette.objects.filter().annotate(fiche_count=Count('fiche', distinct=True) + Count('entreeagenda', distinct=True)).order_by(Lower("nom__unaccent"))
    etiquettes = annoter_class_nuage(etiquettes)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "etiquettes", "critere_name": "etiquette",
                                                         "elements": etiquettes, "titre": "Toutes les étiquettes",
                                                         "nom_humain": "étiquette", "nom_humain_pluriel": "étiquettes",
                                                         "entete": get_entete("etiquettes")})


@login_required
def rechercher(request):

    results_fiches = None
    results_agenda = None
    results_glossaire = None
    recherche = None

    if request.method == "GET":
        recherche = request.GET.get('search')
        if recherche != '':
            results_fiches = Fiche.rechercher(recherche)
            results_glossaire = EntreeGlossaire.rechercher(recherche)
            results_agenda = EntreeAgenda.rechercher(recherche)
            results_etiquettes = Etiquette.rechercher(recherche)
            results_themes = Theme.rechercher(recherche)
            results_categories = Categorie.rechercher(recherche)
            results_documents = Document.rechercher(recherche)
            results_entetes = EntetePage.rechercher(recherche)

    return render(request, 'fiches/rechercher.html', {'results_fiches': results_fiches,
                                                      'results_glossaire': results_glossaire,
                                                      'results_agenda': results_agenda,
                                                      'results_etiquettes': results_etiquettes,
                                                      'results_themes': results_themes,
                                                      'results_categories': results_categories,
                                                      'results_documents': results_documents,
                                                      'results_entetes': results_entetes,
                                                      'recherche': recherche,
                                                      "entete": get_entete("recherche")})


@login_required
def glossaire(request):
    return glossaire_page(request, "A")


@login_required
def glossaire_page(request, key):
    if key >= "A" and key <= "Z":
        entrees = EntreeGlossaire.objects.order_by(Lower('entree__unaccent')).filter(entree__istartswith=key)
        extension_titre = "commençant par " + key
    else:
        entrees = EntreeGlossaire.objects.order_by(Lower('entree__unaccent')).exclude(entree__unaccent__iregex=r'^[a-zA-Z].*$')
        extension_titre = "ne commençant pas par une lettre"
    nb_entrees = EntreeGlossaire.objects.count()

    context = {'entrees': entrees, "nb_entrees": nb_entrees, "key": key, "extension_titre": extension_titre,
               'entete': get_entete("glossaire")}
    return render(request, 'fiches/index_entree_glossaire.html', context)


@login_required
def recherche_glossaire(request, txt):
    entrees = EntreeGlossaire.objects.filter(Q(entree=txt) | Q(formes_alternatives__contains=[txt]))
    context = {'entrees': entrees, 'recherche': txt}
    return render(request, 'fiches/entrees_glossaire.html', context)


@login_required
def entree_glossaire(request, id):
    entree = get_object_or_404(EntreeGlossaire, pk=id)
    etiquettes = Etiquette.objects.filter(Q(nom=entree.entree) | Q(nom=entree.formes_alternatives))
    context = {'entree': entree, 'etiquettes': etiquettes}
    return render(request, 'fiches/entree_glossaire.html', context)


@login_required
@permission_required("fichier.view_document")
def desk(request):
    entrees = Document.objects.order_by('titre__unaccent')
    context = {'entrees': entrees, 'entete': get_entete("desk")}
    return render(request, 'fiches/desk.html', context)


@login_required
@permission_required("fichier.view_document")
def document(request, id):
    entree = get_object_or_404(Document, pk=id)
    context = {'entree': entree}
    return render(request, 'fiches/document.html', context)


@login_required
def duplicate_object(request, classname, id):
    local_classname = "entreeagenda" if classname == "agenda" else classname
    if not request.user.has_perm("fichier.add_" + local_classname.replace("_", "")):
        return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    return edit_object(request, classname, id, True)


@login_required
def edit_object(request, classname, id=None, clone=False):
    single_reverse = False

    if classname == "document":
        nom_classe = "document"
        titre_add = "Création d\'un document du desk"
        titre_edition = "Édition du document du desk"
        titre_clone = "Duplication du document du desk"
        message_add_success = 'Le document du desk "%s" a été ajouté avec succès.'
        message_edit_success = 'Le document du desk "%s" a été modifié avec succès.'
        classe = Document
        classeform = DocumentForm
        reverse_url = 'fichier:document'
        reverse_url_cancel = 'fichier:desk'
    elif classname == "glossaire":
        nom_classe = "entreeglossaire"
        titre_add = "Création d\'entrée de glossaire"
        titre_edition = "Édition de l\'entrée de glossaire"
        titre_clone = "Duplication de l'entrée de glossaire"
        message_add_success = 'L\'entrée de glossaire "%s" a été ajoutée avec succès.'
        message_edit_success = 'L\'entrée de glossaire "%s" a été modifiée avec succès.'
        classe = EntreeGlossaire
        classeform = EntreeGlossaireForm
        reverse_url = 'fichier:entree_glossaire'
        reverse_url_cancel = 'fichier:glossaire'
    elif classname == "agenda":
        nom_classe = "entreeagenda"
        titre_add = "Création d\'une entrée d'agenda"
        titre_edition = "Édition de l\'entrée d'agenda"
        titre_clone = "Duplication de l'entrée d'agenda"
        message_add_success = 'L\'entrée d\'agenda "%s" a été ajoutée avec succès.'
        message_edit_success = 'L\'entrée d\'agenda "%s" a été modifiée avec succès.'
        classe = EntreeAgenda
        classeform = EntreeAgendaForm
        reverse_url = 'fichier:entree_agenda_pk'
        reverse_url_cancel = 'fichier:agenda'
    elif classname == "fiche":
        nom_classe = "fiche"
        titre_add = "Création d\'une fiche"
        titre_edition = "Édition de la fiche"
        titre_clone = "Duplication de la fiche"
        message_add_success = 'La fiche "%s" a été ajoutée avec succès.'
        message_edit_success = 'La fiche "%s" a été modifiée avec succès.'
        classe = Fiche
        classeform = FicheForm
        reverse_url = 'fichier:detail'
        reverse_url_cancel = 'fichier:index'
    elif classname == "categorie":
        nom_classe = "categorie"
        titre_add = "Création d\'une catégorie"
        titre_edition = "Édition de la catégorie"
        titre_clone = "Duplication de la catégorie"
        message_add_success = 'La catégorie "%s" a été ajoutée avec succès.'
        message_edit_success = 'La catégorie "%s" a été modifiée avec succès.'
        classe = Categorie
        classeform = CategorieForm
        reverse_url = 'fichier:index_categorie'
        reverse_url_cancel = 'fichier:categories'
    elif classname == "theme":
        nom_classe = "theme"
        titre_add = "Création d\'un thème"
        titre_edition = "Édition du thème"
        titre_clone = "Duplication du thème"
        message_add_success = 'Le thème "%s" a été ajouté avec succès.'
        message_edit_success = 'Le thème "%s" a été modifié avec succès.'
        classe = Theme
        classeform = ThemeForm
        reverse_url = 'fichier:themes_alpha'
        reverse_url_cancel = 'fichier:themes_alpha'
        single_reverse = True
    elif classname == "etiquette":
        nom_classe = "etiquette"
        titre_add = "Création d\'une étiquette"
        titre_edition = "Édition de l'étiquette"
        titre_clone = "Duplication de l'étiquette"
        message_add_success = 'L\'étiquette "%s" a été ajoutée avec succès.'
        message_edit_success = 'L\'étiquette "%s" a été modifiée avec succès.'
        classe = Etiquette
        classeform = EtiquetteForm
        reverse_url = 'fichier:etiquettes_alpha'
        reverse_url_cancel = 'fichier:etiquettes_alpha'
        single_reverse = True
    elif classname == "niveau":
        nom_classe = "niveau"
        titre_add = "Création d\'un niveau"
        titre_edition = "Édition du niveau"
        titre_clone = "Duplication du niveau"
        message_add_success = 'Le niveau "%s" a été ajouté avec succès.'
        message_edit_success = 'Le niveau "%s" a été modifié avec succès.'
        classe = Niveau
        classeform = NiveauForm
        reverse_url = 'fichier:index_niveau'
        reverse_url_cancel = 'fichier:index'
    elif classname == "entete_page":
        nom_classe = "entetepage"
        titre_add = "Création d'une entête"
        if request.method == 'GET' and "page" in request.GET:
            titre_add += " de la page " + EntetePage.nom_page(request.GET["page"])
        titre_edition = "Édition de l'entête"
        titre_clone = "Duplication de l'entête"
        message_add_success = 'L\'entête de "%s" a été ajoutée avec succès.'
        message_edit_success = 'L\'entête de "%s" a été modifiée avec succès.'
        classe = EntetePage
        classeform = EntetePageForm
        reverse_url = '^'
        reverse_url_cancel = '^'
    else:
        raise Http404("Donnée inconnue")

    if not request.user.has_perm("fichier.change_" + nom_classe):
        return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    complements = {}

    # Retrieve object
    if id is None:
        # "Add" mode
        object = None
        required_permission = 'fichier.add_' + nom_classe
        titre = titre_add
    else:
        # Change mode
        object = get_object_or_404(classe, pk=id)
        if clone:
            object.id = None
            titre = titre_clone + " " + str(object)
            required_permission = 'fichier.add_' + nom_classe
            if classname == "agenda":
                object.date = None
            if classname == "document":
                object.titre += " (copie)"
        else:
            titre = titre_edition + " " + str(object)
            required_permission = 'fichier.change_' + nom_classe

    if classname == "agenda":
        if object and object.id is not None:
            complements["not_available_dates"] = EntreeAgenda.objects.exclude(id=object.id)
        else:
            complements["not_available_dates"] = EntreeAgenda.objects.all()

    # Check user permissions
    if not request.user.is_authenticated or not request.user.has_perm(required_permission):
        raise PermissionDenied

    template_name = 'fiches/edit_form.html'
    header = ""

    if request.method == 'POST':

        params_reverse_url = []
        simple_reverse = False
        if reverse_url == "^":
            simple_reverse = True
            reverse_url = EntetePage.page_url_name(request.POST["page"])
            params_reverse_url = EntetePage.page_url_parameters(request.POST["page"])
        if reverse_url_cancel == "^":
            reverse_url_cancel = EntetePage.page_url_name(request.POST["page"])

        if "annuler" in request.POST:
            messages.info(request, "Édition annulée")
            if object:
                if not simple_reverse:
                    return HttpResponseRedirect(reverse(reverse_url, args=[id]))
                else:
                    return HttpResponseRedirect(reverse(reverse_url, args=params_reverse_url))
            else:
                return HttpResponseRedirect(reverse(reverse_url_cancel, args=params_reverse_url))
        else:
            form = classeform(request.POST, request.FILES, instance=object, user=request.user)
            if form.is_valid():
                object = form.save()
                if id is None or clone:
                    message = message_add_success % object
                else:
                    message = message_edit_success % object
                messages.success(request, message)
                if single_reverse or simple_reverse:
                    return HttpResponseRedirect(reverse(reverse_url, args=params_reverse_url))
                else:
                    return HttpResponseRedirect(reverse(reverse_url, args=[object.id]))
            else:
                if classname == "glossaire" and "entree" in form.errors and form.data["entree"] != "":
                    entree = EntreeGlossaire.objects.filter(entree=form.data["entree"])[0]
                    url = reverse_lazy("fichier:entree_glossaire", kwargs={'id': entree.id})
                    header = "<ul><li>Les modifications que vous avez faites n'ont pas été enregistrées car nous avons identifié que l'entrée <a href=\"" + url + "\">" + form.data["entree"] + "</a> existait déjà.</li></ul>"

    else:
        if request.GET:
            form = classeform(instance=object, data=request.GET, user=request.user)
            if classname == "agenda" and "date" in request.GET and request.GET["date"]:
                titre = titre_edition + " " + request.GET["date"]
                ephemeride = Ephemeride(date.fromisoformat(to_iso(request.GET["date"])))
                complements = {**complements, "ephemeride": ephemeride}
        else:
            form = classeform(instance=object, user=request.user)

    footer = "<ul><li>Les champs dont les noms sont en gras sont des champs requis.</li><li>* : " + message_sortable + "</i><li>** : " + message_glossaire + "</li></ul>"

    params = {
        'titre': titre,
        'object': object,
        'form': form,
        'validation': not bool(request.GET),
        'add': not object or object.id is None,
        'nom_classe': nom_classe,
        'footer': footer,
        'header': header
    }
    return render(request, template_name, {**params, **complements})


@login_required
def agenda_current_month(request):
    return agenda_month(request, timezone.now().year, timezone.now().month)


@login_required
def agenda_year(request, year):
    entrees = EntreeAgenda.objects.filter(date__year=year)
    aa = Agenda(entrees, 0, 'fr_FR.UTF-8')
    context = {'agenda': aa, "year": year}
    return render(request, 'fiches/agenda_year.html', context)


@login_required
def agenda_month(request, year, month):
    entrees = EntreeAgenda.objects.filter(date__year=year, date__month=month)
    aa = Agenda(entrees, 0, 'fr_FR.UTF-8')
    context = {'agenda': aa, "year": year, "month": month,
               "entete_mois": get_entete("agenda/" + str(year) + "/" + str(month) + "/"),
               "entete_mois_annee": year, "entete_mois_mois": Agenda.month_name[int(month)]}
    return render(request, 'fiches/agenda_month.html', context)


@login_required
def agenda_month_details(request, year, month):
    entrees = EntreeAgenda.objects.filter(date__year=year, date__month=month).order_by("date")
    context = {'entrees': entrees, "year": year, "month": month, "entete": get_entete("agenda/" + str(year) + "/" + str(month) + "/")}
    return render(request, 'fiches/agenda_month_details.html', context)


def _entree_agenda(request, entree):
    context = {'entree': entree, "ephemeride": Ephemeride(entree)}
    return render(request, 'fiches/entree_agenda.html', context)


@login_required
def entree_agenda_pk(request, id):
    entree = get_object_or_404(EntreeAgenda, pk=id)
    return _entree_agenda(request, entree)


@login_required
def entree_agenda(request, year, month, day):
    d = datetime(year, month, day)
    entree = EntreeAgenda.objects.filter(date=d)
    if entree:
        return _entree_agenda(request, entree[0])
    else:
        return HttpResponseRedirect(reverse("fichier:object_add", args=["agenda"]) + "?date=" + "/".join(map(str, [year, month, day])))


class FichesViewPDF(WeasyTemplateResponseMixin, ListView):
    template_name = 'fiches/fiches_pdf.html'

    model = Fiche

    def get_pdf_filename(self):
        from django.utils import timezone
        return 'fiches 365 {at}.pdf'.format(
            at=str(timezone.now().strftime("%d-%m-%Y %H:%M")),
        )


class FicheViewPDF(LoginRequiredMixin, WeasyTemplateResponseMixin, DetailView):

    template_name = 'fiches/detail_pdf.html'

    model = Fiche

    def get_pdf_filename(self):
        from django.utils import timezone
        return '{nom} {at}.pdf'.format(
            nom=str(self.get_object().get_simple_name()).replace('\'', '\\\''),
            at=str(self.get_object().date_derniere_modification.strftime("%d-%m-%Y %H:%M:%S")),
        )


class EntreeAgendaViewPDF(LoginRequiredMixin, WeasyTemplateResponseMixin, DetailView):

    template_name = 'fiches/entree_agenda_pdf.html'

    model = EntreeAgenda

    def get_pdf_filename(self):
        from django.utils import timezone
        return 'Entrée agenda {nom} version du {at}.pdf'.format(
            nom=str(self.get_object().__str__()).replace('\'', '\\\''),
            at=str(self.get_object().date_derniere_modification.strftime("%d-%m-%Y %H:%M:%S")),
        )


class DeleteObjectView(LoginRequiredMixin, DeleteView):
    template_name = "fiches/delete_form.html"

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            url = reverse_lazy(self.cancel_url, kwargs={'id': self.kwargs['pk']})
            return HttpResponseRedirect(url)
        else:
            return super(DeleteObjectView, self).post(request, *args, **kwargs)


@method_decorator(permission_required("fichier.delete_theme"), name='dispatch')
class DeleteThemeView(DeleteObjectView):
    model = Theme
    success_url = reverse_lazy("fichier:themes")
    cancel_url = "fichier:entree_theme"


@method_decorator(permission_required("fichier.delete_etiquette"), name='dispatch')
class DeleteEtiquetteView(DeleteObjectView):
    model = Etiquette
    success_url = reverse_lazy("fichier:etiquettes")
    cancel_url = "fichier:index_etiquette"


@method_decorator(permission_required("fichier.delete_fiche"), name='dispatch')
class DeleteFicheView(DeleteObjectView):
    model = Fiche
    success_url = reverse_lazy("fichier:index")
    cancel_url = "fichier:detail"


@method_decorator(permission_required("fichier.delete_entreeglossaire"), name='dispatch')
class DeleteEntreeGlossaireView(DeleteObjectView):
    model = EntreeGlossaire
    success_url = reverse_lazy("fichier:glossaire")
    cancel_url = "fichier:entree_glossaire"


@method_decorator(permission_required("fichier.delete_entreeagenda"), name='dispatch')
class DeleteEntreeAgendaView(DeleteObjectView):
    model = EntreeAgenda
    success_url = reverse_lazy("fichier:agenda")
    cancel_url = "fichier:entree_agenda_pk"


@method_decorator(permission_required("fichier.delete_categorie"), name='dispatch')
class DeleteCategorieView(DeleteObjectView):
    model = Categorie
    success_url = reverse_lazy("fichier:categories")
    cancel_url = "fichier:index_categorie"


@method_decorator(permission_required("fichier.delete_document"), name='dispatch')
class DeleteDocumentView(DeleteObjectView):
    model = Document
    success_url = reverse_lazy("fichier:desk")
    cancel_url = "fichier:document"


def page_not_found_view(request, exception=None):
    return render(request, 'fiches/404.html', {"exception": exception})


def rest_api(request, classname):
    classes = {"theme": Theme, "etiquette": Etiquette}

    def json_context(dictionary):
        return {"json": json.dumps(dictionary)}

    if not request.user.has_perm("fichier.add_" + classname):
        return render(request, 'fiches/json.html', json_context({"error": "Vous n'avez pas l'autorisation de réaliser cette opération."}))

    if classname not in classes:
        return render(request, 'fiches/json.html', json_context({"error": "class not found"}))

    if request.method == 'POST':
        body = json.loads(request.body)

        if "nom" not in body:
            return render(request, 'fiches/json.html', json_context({"error": "new name not found"}))

        nom = body["nom"]

        try:
            b = classes[classname](nom=nom)
            b.save()
        except IntegrityError:
            return render(request, 'fiches/json.html', json_context({"error": "L'entrée existe déjà. Veuillez choisir cette entrée dans la liste des entrées existantes."}))

        return render(request, 'fiches/json.html', json_context({"id": b.id, "nom": b.nom}))


@login_required
@permission_required("fichier.change_entreeagenda")
def entree_agenda_invert_with(request, pk):
    element1 = get_object_or_404(EntreeAgenda, pk=pk)

    if request.method == 'POST':
        if "annuler" in request.POST:
            messages.info(request, "Inversion annulée")
            return HttpResponseRedirect(reverse("fichier:entree_agenda_pk", args=[pk]))
        else:
            form = EntreeAgendaInvertWithForm(data=request.POST, date1=element1)
            if form.is_valid():
                element2 = form.cleaned_data["element2"]
                date1 = element1.date
                date2 = element2.date
                element2.date = date1
                element2.save()
                element1.date = date2
                element1.save()

                messages.success(request, mark_safe('Inversion réussie entre les deux dates <a href="' + reverse("fichier:entree_agenda_pk", args=[element1.id]) + '">' + str(element1) + '</a> et <a href="' + reverse("fichier:entree_agenda_pk", args=[element2.id]) + '">' + str(form.cleaned_data["element2"]) + "</a>"))
                return HttpResponseRedirect(reverse("fichier:entree_agenda_pk", args=[pk]))
    else:
        form = EntreeAgendaInvertWithForm(date1=element1)

    return render(request, "fiches/inverser_entree_agenda_avec.html", {
        'form': form,
        'entree1': element1
    })


@login_required
@permission_required("fichier.change_entreeagenda")
def entree_agenda_invert(request):
    if request.method == 'POST':
        if "annuler" in request.POST:
            messages.info(request, "Inversion annulée")
            return HttpResponseRedirect(reverse("fichier:agenda"))
        else:
            form = EntreeAgendaInvertForm(data=request.POST)
            if form.is_valid():
                element1 = form.cleaned_data["element1"]
                element2 = form.cleaned_data["element2"]
                date1 = element1.date
                date2 = element2.date
                element2.date = date1
                element2.save()
                element1.date = date2
                element1.save()

                messages.success(request, mark_safe('Inversion réussie entre les deux dates <a href="' + reverse("fichier:entree_agenda_pk", args=[element1.id]) + '">' + str(form.cleaned_data["element1"]) + '</a> et <a href="' + reverse("fichier:entree_agenda_pk", args=[element2.id]) + '">' + str(form.cleaned_data["element2"]) + "</a>"))
                return HttpResponseRedirect(reverse("fichier:agenda"))
    else:
        form = EntreeAgendaInvertForm()

    return render(request, "fiches/inverser_entree_agenda.html", {
        'form': form,
    })


@login_required
def merge(request, classname):

    if classname == "theme":
        pluriel = "thèmes"
        classform = ThemeMergeForm
        reverse_url_main = "fichier:themes"
        field_fiche = "themes"
        field_agenda = "themes"
        nom_classe = "theme"
    elif classname == "etiquette":
        pluriel = "étiquettes"
        classform = EtiquetteMergeForm
        reverse_url_main = "fichier:etiquettes"
        field_fiche = "etiquettes"
        field_agenda = "etiquettes"
        nom_classe = "etiquette"
    else:
        return Http404("Impossible de lancer la fusion")

    if not request.user.has_perm("fichier.change_" + nom_classe):
        return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    if request.method == 'POST':
        if "annuler" in request.POST:
            messages.info(request, "Fusion annulée")
            return HttpResponseRedirect(reverse(reverse_url_main))
        else:
            form = classform(data=request.POST)
            if form.is_valid():
                for fiche in Fiche.objects.filter(**{field_fiche: form.cleaned_data["element2"].id}):
                    if classname == "theme":
                        fiche.themes.add(form.cleaned_data["element1"])
                        fiche.themes.remove(form.cleaned_data["element2"])
                    elif classname == "etiquette":
                        fiche.etiquettes.add(form.cleaned_data["element1"])
                        fiche.etiquettes.remove(form.cleaned_data["element2"])
                if classname == "theme" or classname == "etiquette":
                    for entree in EntreeAgenda.objects.filter(**{field_agenda: form.cleaned_data["element2"].id}):
                        if classname == "theme":
                            entree.themes.add(form.cleaned_data["element1"])
                            entree.themes.remove(form.cleaned_data["element2"])
                        elif classname == "etiquette":
                            entree.etiquettes.add(form.cleaned_data["element1"])
                            entree.etiquettes.remove(form.cleaned_data["element2"])

                if classname == "theme":
                    Theme.objects.filter(pk=form.cleaned_data["element2"].id).delete()
                elif classname == "etiquette":
                    Etiquette.objects.filter(pk=form.cleaned_data["element2"].id).delete()

                messages.success(request, "Fusion réussie entre les deux " + pluriel + " " + form.cleaned_data["element1"].nom + " et " + form.cleaned_data["element2"].nom)
                return HttpResponseRedirect(reverse(reverse_url_main))
    else:
        form = classform()

    return render(request, "fiches/merge.html", {
        'titre': "Fusion de deux " + pluriel,
        'form': form,
        'pluriel': pluriel
    })


@login_required
def simple_modifications_page(request, classname, key):

    liste_entrees = []
    if classname in ["agenda", ""]:
        liste_entrees.append(EntreeAgenda.objects.all())
    if classname in ["glossaire", ""]:
        liste_entrees.append(EntreeGlossaire.objects.all())
    if classname in ["fiches", ""]:
        liste_entrees.append(Fiche.objects.all())

    entrees = sorted(chain(*liste_entrees),
                     key=lambda entree: entree.date_derniere_modification, reverse=True)
    step = 20
    es = Paginator(entrees, step)

    return render(request, "fiches/modifications.html", {
                  "elements": es.page(key).object_list,
                  "url_key_paginator": "fichier:modifications_page" if classname == "" else "fichier:simple_modifications_page",
                  "p_id": key,
                  "classname": classname,
                  "paginator": es})


@login_required
def modifications(request):
    return modifications_page(request, 1)


@login_required
def modifications_page(request, key):
    return simple_modifications_page(request, "", key)


@login_required
def simple_modifications(request, classname):
    return simple_modifications_page(request, classname, 1)


@login_required
def liens_sortants(request):
    entrees_agenda = EntreeAgenda.objects.filter(urls__len__gt=0)
    entrees_glossaire = EntreeGlossaire.objects.filter(urls__len__gt=0)
    fiches = Fiche.objects.filter(urls__len__gt=0)

    return render(request, "fiches/liens_sortants.html", {"entrees_agenda": entrees_agenda,
                  "entrees_glossaire": entrees_glossaire, "fiches": fiches, "entete": get_entete("liens_sortants")})
