from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.template import loader
from .models import Fiche, Niveau, Categorie, Auteur, CategorieLibre, Theme, MotCle, EntreeGlossaire, EntreeAgenda, Document
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Q, Case, When, IntegerField, Max, F, ExpressionWrapper, Value, FloatField
from decimal import Decimal
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.http import Http404, HttpResponseRedirect
from .forms import FicheForm, EntreeGlossaireForm, EntreeAgendaForm, CategorieForm, ThemeForm, MotCleForm, CategorieLibreForm, ThemeMergeForm, MotCleMergeForm, CategorieLibreMergeForm, NiveauForm, DocumentForm
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.generic.edit import DeleteView
import json
from datetime import datetime, timedelta
from django.db import IntegrityError
from .utils import message_glossaire, message_sortable
from django.db.models.functions import Ceil, Cast, Lower

from django.views.generic import DetailView

from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import WeasyTemplateResponse

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import Agenda, Ephemeride, table, arrayToString

import logging
logger = logging.getLogger(__name__)


def annoter_class_nuage(objects):
    nb_max = 5
    nb = objects.aggregate(Max("fiche_count"))["fiche_count__max"]
    logger.warning("count max " + str(nb))
    return objects.annotate(classe_nuage=Cast(Ceil(Cast(Value(nb_max) * F('fiche_count'), FloatField()) / Value(nb)), IntegerField())). \
        annotate(max_classe_nuage=Value(nb_max))


@login_required
def accueil(request):
    nbfiches = 5
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')[:5]
    nbfiches = latest_fiche_list.count()

    nbentreesglossaire = EntreeGlossaire.objects.count()

    niveaux = Niveau.objects.annotate(fiche_count=Count('fiche')).order_by("ordre")

    nbcategories = 9
    categories = annotate_categories_par_niveau()[:nbcategories]
    nbcategories = categories.count()

    auteurs = Auteur.objects.annotate(fiche_count=Count('fiche'))

    nbthemes = 15
    themes = Theme.objects.annotate(fiche_count=Count('fiche')).order_by("-fiche_count", "nom__unaccent")[:nbthemes]
    nbthemes = themes.count()

    motcles = MotCle.objects.annotate(fiche_count=Count('fiche', distinct=True) + Count('entreeagenda', distinct=True)).order_by("nom__unaccent")
    motcles = annoter_class_nuage(motcles)

    nbcategorieslibres = 9
    categories_libres = CategorieLibre.objects.annotate(fiche_count=Count('fiche')).order_by("-fiche_count", "nom__unaccent")[:nbcategorieslibres]
    nbcategorieslibres = categories_libres.count()

    entrees_agenda = EntreeAgenda.objects.filter(date=timezone.now())
    if entrees_agenda.count() == 0:
        entree_agenda = Ephemeride(timezone.now())
    else:
        entree_agenda = entrees_agenda[0]

    context = {'fiche_list': latest_fiche_list, 'nbfiches': nbfiches,
               "nbfichestotal": Fiche.objects.count(), "niveaux": niveaux,
               "categories": categories, "nbcategories": nbcategories,
               "auteurs": auteurs,
               "themes": themes, "nbthemes": nbthemes,
               "motcles": motcles,
               "categories_libres": categories_libres, "nbcategorieslibres": nbcategorieslibres,
               "nbentreesglossaire": nbentreesglossaire,
               "entree_agenda": entree_agenda}
    return render(request, 'fiches/accueil.html', context)


@login_required
def index(request):
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')
    context = {'fiche_list': latest_fiche_list}
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
def index_niveau(request, id):
    niveau = get_object_or_404(Niveau, pk=id)
    fiches = Fiche.objects.filter(niveau=niveau)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "niveau", "critere": niveau,
                                                             "critere_human": "du niveau", "critere_nom": str(niveau),
                                                             "fiche_list": fiches})


@login_required
def index_niveau_detail(request, id1, id2):
    niveau = get_object_or_404(Niveau, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(niveau=niveau)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "niveau", "critere": niveau,
                                                                    "critere_human": "du niveau", "critere_nom": str(niveau),
                                                                    "fiche_list": fiches, "fiche": fiche})


@login_required
def index_categorie(request, id):
    categorie = get_object_or_404(Categorie, pk=id)
    fiches = Fiche.objects.filter(Q(categorie1=categorie) | Q(categorie2=categorie) | Q(categorie3=categorie))
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "categorie", "critere": categorie,
                                                             "critere_human": "de la cat??gorie", "critere_nom": str(categorie),
                                                             "fiche_list": fiches})


@login_required
def index_categorie_detail(request, id1, id2):
    categorie = get_object_or_404(Categorie, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(Q(categorie1=categorie) | Q(categorie2=categorie) | Q(categorie3=categorie))
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "categorie", "critere": categorie,
                                                                    "critere_human": "de la cat??gorie", "critere_nom": str(categorie),
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
    categories_libres = annotate_categories_par_niveau_simple(CategorieLibre.objects).order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                   "elements": categories, "titre": "Toutes les cat??gories",
                                                   "nom_humain": "cat??gorie", "nom_humain_pluriel": "cat??gories",
                                                   "visu_code": "basic", "visu": "tri??es par nombre total de fiches",
                                                   "elements_second": categories_libres, "nom_humain_second": "cat??gorie libre",
                                                   "nom_humain_second_pluriel": "cat??gories libres",
                                                   "critere_name_second": "categorie_libre"})


@login_required
def categories_alpha(request):
    categories = annotate_categories_par_niveau_complet().order_by("-fiche_count").order_by(Lower("code__unaccent"))
    categories_libres = annotate_categories_par_niveau_simple(CategorieLibre.objects).order_by("nom__unaccent")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                   "elements": categories, "titre": "Toutes les cat??gories",
                                                   "nom_humain": "cat??gorie", "nom_humain_pluriel": "cat??gories",
                                                   "visu_code": "alpha", "visu": "par ordre alphab??tique",
                                                   "elements_second": categories_libres, "nom_humain_second": "cat??gorie libre",
                                                   "nom_humain_second_pluriel": "cat??gories libres",
                                                   "critere_name_second": "categorie_libre"})


@login_required
def categories_nuage(request):
    categories = annotate_categories_par_niveau().order_by("code__unaccent")
    categories = annoter_class_nuage(categories)
    categories_libres = CategorieLibre.objects.filter().annotate(fiche_count=Count('fiche', distinct=True)).order_by("nom__unaccent")
    categories_libres = annoter_class_nuage(categories_libres)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                         "elements": categories, "titre": "Toutes les cat??gories",
                                                         "nom_humain": "cat??gorie", "nom_humain_pluriel": "cat??gories",
                                                         "elements_second": categories_libres, "nom_humain_second": "cat??gorie libre",
                                                         "nom_humain_second_pluriel": "cat??gories libres",
                                                         "critere_name_second": "categorie_libre"})


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


@login_required
def index_categorie_libre(request, id):
    categorie_libre = get_object_or_404(CategorieLibre, pk=id)
    fiches = Fiche.objects.filter(categories_libres=categorie_libre)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "categorie_libre", "critere": categorie_libre,
                                                             "critere_human": "de la cat??gorie libre", "critere_nom": str(categorie_libre),
                                                             "fiche_list": fiches})


@login_required
def index_categorie_libre_detail(request, id1, id2):
    categorie_libre = get_object_or_404(CategorieLibre, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(categories_libres=categorie_libre)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "categorie_libre", "critere": categorie_libre,
                                                                    "critere_human": "de la cat??gorie libre", "critere_nom": str(categorie_libre),
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
    agendas = EntreeAgenda.objects.filter(themes=theme)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "theme", "critere": theme,
                                                             "critere_human": "du th??me",
                                                             "critere_nom": str(theme), "fiche_list": fiches,
                                                             "entreesagenda": agendas})


@login_required
def index_theme_detail(request, id1, id2):
    theme = get_object_or_404(Theme, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(themes=theme)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "theme", "critere": theme,
                                                                    "critere_human": "du th??me", "critere_nom": str(theme),
                                                                    "fiche_list": fiches, "fiche": fiche})


@login_required
def themes(request):
    themes = annotate_categories_par_niveau_simple(Theme.objects, True).order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les th??mes",
                                                   "nom_humain": "th??me", "nom_humain_pluriel": "th??mes",
                                                   "visu_code": "basic", "visu": "tri??es par nombre de fiches"})


@login_required
def themes_alpha(request):
    themes = annotate_categories_par_niveau_simple(Theme.objects, True).order_by("nom__unaccent")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les th??mes",
                                                   "nom_humain": "th??me", "nom_humain_pluriel": "th??mes",
                                                   "visu_code": "alpha", "visu": "par ordre alphab??tique"})


@login_required
def themes_nuage(request):
    themes = Theme.objects.filter().annotate(fiche_count=Count('fiche', distinct=True) + Count('entreeagenda', distinct=True)). \
        order_by("nom__unaccent")
    themes = annoter_class_nuage(themes)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                         "elements": themes, "titre": "Tous les th??mes",
                                                         "nom_humain": "th??me", "nom_humain_pluriel": "th??mes"})


@login_required
def index_motcle(request, id):
    motcle = get_object_or_404(MotCle, pk=id)
    fiches = Fiche.objects.filter(mots_cles=motcle)
    agendas = EntreeAgenda.objects.filter(motscles=motcle)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "motcle", "critere": motcle,
                                                             "critere_human": "du mot-cl??", "critere_nom": str(motcle),
                                                             "fiche_list": fiches, "entreesagenda": agendas})


@login_required
def index_motcle_detail(request, id1, id2):
    motcle = get_object_or_404(MotCle, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(mots_cles=motcle)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "motcle", "critere": motcle,
                                                                    "critere_human": "du mot-cl??", "critere_nom": str(motcle),
                                                                    "fiche_list": fiches, "fiche": fiche})


@login_required
def motscles(request):
    motscles = annotate_categories_par_niveau_simple(MotCle.objects, True).order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                   "elements": motscles, "titre": "Tous les mots-cl??s",
                                                   "nom_humain": "mot-cl??", "nom_humain_pluriel": "mots-cl??s",
                                                   "visu_code": "basic", "visu": "tri??es par nombre de fiches"})


@login_required
def motscles_alpha(request):
    motscles = annotate_categories_par_niveau_simple(MotCle.objects, True).order_by("nom__unaccent")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                   "elements": motscles, "titre": "Tous les mots-cl??s",
                                                   "nom_humain": "mot-cl??", "nom_humain_pluriel": "mots-cl??s",
                                                   "visu_code": "alpha", "visu": "par ordre alphab??tique"})


@login_required
def motscles_nuage(request):
    motscles = MotCle.objects.filter().annotate(fiche_count=Count('fiche', distinct=True) + Count('entreeagenda', distinct=True)).order_by("nom__unaccent")
    motscles = annoter_class_nuage(motscles)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                         "elements": motscles, "titre": "Tous les mots-cl??s",
                                                         "nom_humain": "mot-cl??", "nom_humain_pluriel": "mots-cl??s"})


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
            results_motscles = MotCle.rechercher(recherche)
            results_themes = Theme.rechercher(recherche)
            results_categories_libres = CategorieLibre.rechercher(recherche)
            results_categories = Categorie.rechercher(recherche)
            results_documents = Document.rechercher(recherche)

    return render(request, 'fiches/rechercher.html', {'results_fiches': results_fiches,
                                                      'results_glossaire': results_glossaire,
                                                      'results_agenda': results_agenda,
                                                      'results_motscles': results_motscles,
                                                      'results_themes': results_themes,
                                                      'results_categories': results_categories,
                                                      'results_categories_libres': results_categories_libres,
                                                      'results_documents': results_documents,
                                                      'recherche': recherche})


@login_required
def glossaire(request):
    entrees = EntreeGlossaire.objects.order_by('entree__unaccent')
    context = {'entrees': entrees}
    return render(request, 'fiches/index_entree_glossaire.html', context)


@login_required
def entree_glossaire(request, id):
    entree = get_object_or_404(EntreeGlossaire, pk=id)
    context = {'entree': entree}
    return render(request, 'fiches/entree_glossaire.html', context)


@login_required
def desk(request):
    entrees = Document.objects.order_by('titre__unaccent')
    context = {'entrees': entrees}
    return render(request, 'fiches/desk.html', context)


@login_required
def document(request, id):
    entree = get_object_or_404(Document, pk=id)
    context = {'entree': entree}
    return render(request, 'fiches/document.html', context)


@login_required
def edit_object(request, classname, id=None):
    single_reverse = False

    if classname == "document":
        nom_classe = "document"
        titre_add = "Cr??ation d\'un document du desk"
        titre_edition = "??dition du document du desk"
        message_add_success = 'Le document du desk "%s" a ??t?? ajout?? avec succ??s.'
        message_edit_success = 'Le document du desk "%s" a ??t?? modifi?? avec succ??s.'
        classe = Document
        classeform = DocumentForm
        reverse_url = 'fichier:document'
    elif classname == "glossaire":
        nom_classe = "entreeglossaire"
        titre_add = "Cr??ation d\'entr??e de glossaire"
        titre_edition = "??dition de l\'entr??e de glossaire"
        message_add_success = 'L\'entr??e de glossaire "%s" a ??t?? ajout??e avec succ??s.'
        message_edit_success = 'L\'entr??e de glossaire "%s" a ??t?? modifi??e avec succ??s.'
        classe = EntreeGlossaire
        classeform = EntreeGlossaireForm
        reverse_url = 'fichier:entree_glossaire'
    elif classname == "agenda":
        nom_classe = "entreeagenda"
        titre_add = "Cr??ation d\'une entr??e d'agenda"
        titre_edition = "??dition de l\'entr??e d'agenda"
        message_add_success = 'L\'entr??e d\'agenda "%s" a ??t?? ajout??e avec succ??s.'
        message_edit_success = 'L\'entr??e d\'agenda "%s" a ??t?? modifi??e avec succ??s.'
        classe = EntreeAgenda
        classeform = EntreeAgendaForm
        reverse_url = 'fichier:entree_agenda_pk'
    elif classname == "fiche":
        nom_classe = "fiche"
        titre_add = "Cr??ation d\'une fiche"
        titre_edition = "??dition de la fiche"
        message_add_success = 'La fiche "%s" a ??t?? ajout??e avec succ??s.'
        message_edit_success = 'La fiche "%s" a ??t?? modifi??e avec succ??s.'
        classe = Fiche
        classeform = FicheForm
        reverse_url = 'fichier:detail'
    elif classname == "categorie":
        nom_classe = "categorie"
        titre_add = "Cr??ation d\'une cat??gorie"
        titre_edition = "??dition de la cat??gorie"
        message_add_success = 'La cat??gorie "%s" a ??t?? ajout??e avec succ??s.'
        message_edit_success = 'La cat??gorie "%s" a ??t?? modifi??e avec succ??s.'
        classe = Categorie
        classeform = CategorieForm
        reverse_url = 'fichier:index_categorie'
    elif classname == "theme":
        nom_classe = "theme"
        titre_add = "Cr??ation d\'un th??me"
        titre_edition = "??dition du th??me"
        message_add_success = 'Le th??me "%s" a ??t?? ajout?? avec succ??s.'
        message_edit_success = 'Le th??me "%s" a ??t?? modifi?? avec succ??s.'
        classe = Theme
        classeform = ThemeForm
        reverse_url = 'fichier:themes_alpha'
        single_reverse = True
    elif classname == "motcle":
        nom_classe = "motcle"
        titre_add = "Cr??ation d\'un mot-cl??"
        titre_edition = "??dition du mot-cl??"
        message_add_success = 'Le mot-cl?? "%s" a ??t?? ajout?? avec succ??s.'
        message_edit_success = 'Le mot-cl?? "%s" a ??t?? modifi?? avec succ??s.'
        classe = MotCle
        classeform = MotCleForm
        reverse_url = 'fichier:motscles_alpha'
        single_reverse = True
    elif classname == "categorie_libre":
        nom_classe = "categorie_libre"
        titre_add = "Cr??ation d\'une cat??gorie libre"
        titre_edition = "??dition d'une cat??gorie libre"
        message_add_success = 'La cat??gorie libre "%s" a ??t?? ajout??e avec succ??s.'
        message_edit_success = 'La cat??gorie libre "%s" a ??t?? modifi??e avec succ??s.'
        classe = CategorieLibre
        classeform = CategorieLibreForm
        reverse_url = 'fichier:index_categorie_libre'
    elif classname == "niveau":
        nom_classe = "niveau"
        titre_add = "Cr??ation d\'un niveau"
        titre_edition = "??dition d'un niveau"
        message_add_success = 'Le niveau "%s" a ??t?? ajout?? avec succ??s.'
        message_edit_success = 'Le niveau "%s" a ??t?? modifi?? avec succ??s.'
        classe = Niveau
        classeform = NiveauForm
        reverse_url = 'fichier:index_niveau'
    else:
        raise Http404("Donn??e inconnue")

    # Retrieve object
    if id is None:
        # "Add" mode
        object = None
        required_permission = 'fichier.add_' + nom_classe
        titre = titre_add
    else:
        # Change mode
        object = get_object_or_404(classe, pk=id)
        required_permission = 'fichier.change_' + nom_classe
        titre = titre_edition + " " + str(object)

    # Check user permissions
    if not request.user.is_authenticated or not request.user.has_perm(required_permission):
        raise PermissionDenied

    template_name = 'fiches/edit_form.html'
    header = ""

    if request.method == 'POST':
        if "annuler" in request.POST:
            messages.info(request, "??dition annul??e")
            return HttpResponseRedirect(reverse(reverse_url, args=[object.id]))
        else:
            logger.warning(request.POST)
            form = classeform(instance=object, data=request.POST, user=request.user)
            if form.is_valid():
                object = form.save()
                if id is None:
                    message = message_add_success % object
                else:
                    message = message_edit_success % object
                messages.success(request, message)
                if single_reverse:
                    return HttpResponseRedirect(reverse(reverse_url))
                else:
                    return HttpResponseRedirect(reverse(reverse_url, args=[object.id]))
            else:
                if classname == "glossaire" and "entree" in form.errors and form.data["entree"] != "":
                    entree = EntreeGlossaire.objects.filter(entree=form.data["entree"])[0]
                    url = reverse_lazy("fichier:entree_glossaire", kwargs={'id': entree.id})
                    header = "<ul><li>Les modifications que vous avez faites n'ont pas ??t?? enregistr??es car nous avons identifi?? que l'entr??e <a href=\"" + url + "\">" + form.data["entree"] + "</a> existait d??j??.</li></ul>"

    else:
        if request.GET:
            form = classeform(instance=object, data=request.GET, user=request.user)
            if classname == "agenda" and request.GET["date"]:
                titre = titre_edition + " " + request.GET["date"]
        else:
            form = classeform(instance=object, user=request.user)

    footer = "<ul><li>Les champs dont les noms sont en gras sont des champs requis.</li><li>* : " + message_sortable + "</i><li>** : " + message_glossaire + "</li></ul>"

    return render(request, template_name, {
        'titre': titre,
        'object': object,
        'form': form,
        'validation': not bool(request.GET),
        'add': id is None,
        'nom_classe': nom_classe,
        'footer': footer,
        'header': header
    })


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
    context = {'agenda': aa, "year": year, "month": month}
    return render(request, 'fiches/agenda_month.html', context)


def _entree_agenda(request, entree, d):
    prev_entree = EntreeAgenda.objects.filter(date=d + timedelta(days=1))
    if len(prev_entree) == 0:
        prev_entree = d + timedelta(days=1)
    else:
        prev_entree = prev_entree[0]
    next_entree = EntreeAgenda.objects.filter(date=d - timedelta(days=1))
    if len(next_entree) == 0:
        next_entree = d - timedelta(days=1)
    else:
        next_entree = next_entree[0]
    context = {'entree': entree, 'prev': prev_entree, 'next': next_entree}
    return render(request, 'fiches/entree_agenda.html', context)


@login_required
def entree_agenda_pk(request, id):
    entree = get_object_or_404(EntreeAgenda, pk=id)
    return _entree_agenda(request, entree, entree.date)


@login_required
def entree_agenda(request, year, month, day):
    d = datetime(year, month, day)
    entree = EntreeAgenda.objects.filter(date=d)
    if entree:
        return _entree_agenda(request, entree[0], d)
    else:
        return HttpResponseRedirect(reverse("fichier:object_add", args=["agenda"]) + "?date=" + "/".join(map(str, [year, month, day])))


class FicheViewPDF(LoginRequiredMixin, WeasyTemplateResponseMixin, DetailView):

    template_name = 'fiches/detail_pdf.html'

    model = Fiche

    def get_pdf_filename(self):
        from django.utils import timezone
        return '{nom} {at}.pdf'.format(
            nom=str(self.get_object()).replace('\'', '\\\''),
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


class DeleteCategorieLibreView(DeleteObjectView):
    model = CategorieLibre
    success_url = reverse_lazy("fichier:categories")
    cancel_url = "fichier:entree_categorie_libre"


class DeleteThemeView(DeleteObjectView):
    model = Theme
    success_url = reverse_lazy("fichier:themes")
    cancel_url = "fichier:entree_theme"


class DeleteMotCleView(DeleteObjectView):
    model = MotCle
    success_url = reverse_lazy("fichier:motscles")
    cancel_url = "fichier:entree_motcle"


class DeleteEntreeGlossaireView(DeleteObjectView):
    model = EntreeGlossaire
    success_url = reverse_lazy("fichier:glossaire")
    cancel_url = "fichier:entree_glossaire"


class DeleteEntreeAgendaView(DeleteObjectView):
    model = EntreeAgenda
    success_url = reverse_lazy("fichier:agenda")
    cancel_url = "fichier:entree_agenda"


class DeleteCategorieView(DeleteObjectView):
    model = Categorie
    success_url = reverse_lazy("fichier:categories")
    cancel_url = "fichier:index_categorie"


class DeleteDocumentView(DeleteObjectView):
    model = Document
    success_url = reverse_lazy("fichier:desk")
    cancel_url = "fichier:document"


def page_not_found_view(request, exception=None):
    return render(request, 'fiches/404.html', {"exception": exception})


def rest_api(request, classname):
    classes = {"categorie_libre": CategorieLibre, "theme": Theme, "motcle": MotCle}

    def json_context(dictionary):
        return {"json": json.dumps(dictionary)}

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
            return render(request, 'fiches/json.html', json_context({"error": "L'entr??e existe d??j??. Veuillez choisir cette entr??e dans la liste des entr??es existantes."}))

        return render(request, 'fiches/json.html', json_context({"id": b.id, "nom": b.nom}))


@login_required
def merge(request, classname):
    if classname == "categorie_libre":
        pluriel = "cat??gories libres"
        classform = CategorieLibreMergeForm
        reverse_url_main = "fichier:categories"
        field_fiche = "categories_libres"
    elif classname == "theme":
        pluriel = "th??mes"
        classform = ThemeMergeForm
        reverse_url_main = "fichier:themes"
        field_fiche = "themes"
        field_agenda = "themes"
    elif classname == "motcle":
        pluriel = "mots-cl??s"
        classform = MotCleMergeForm
        reverse_url_main = "fichier:motscles"
        field_fiche = "mots_cles"
        field_agenda = "motscles"
    else:
        return Http404("Impossible de lancer la fusion")

    if request.method == 'POST':
        logger.warning(request.POST)
        if "annuler" in request.POST:
            messages.info(request, "Fusion annul??e")
            return HttpResponseRedirect(reverse(reverse_url_main))
        else:
            form = classform(data=request.POST)
            if form.is_valid():
                for fiche in Fiche.objects.filter(**{field_fiche: form.cleaned_data["element2"].id}):
                    if classname == "theme":
                        fiche.themes.add(form.cleaned_data["element1"])
                        fiche.themes.remove(form.cleaned_data["element2"])
                    elif classname == "motcle":
                        fiche.mots_cles.add(form.cleaned_data["element1"])
                        fiche.mots_cles.remove(form.cleaned_data["element2"])
                    elif classname == "categorie_libre":
                        fiche.categories_libres.add(form.cleaned_data["element1"])
                        fiche.categories_libres.remove(form.cleaned_data["element2"])
                if classname == "theme" or classname == "motcle":
                    for entree in EntreeAgenda.objects.filter(**{field_agenda: form.cleaned_data["element2"].id}):
                        if classname == "theme":
                            entree.themes.add(form.cleaned_data["element1"])
                            entree.themes.remove(form.cleaned_data["element2"])
                        elif classname == "motcle":
                            entree.motscles.add(form.cleaned_data["element1"])
                            entree.motscles.remove(form.cleaned_data["element2"])

                if classname == "theme":
                    Theme.objects.filter(pk=form.cleaned_data["element2"].id).delete()
                elif classname == "motcle":
                    MotCle.objects.filter(pk=form.cleaned_data["element2"].id).delete()
                elif classname == "categorie_libre":
                    CategorieLibre.objects.filter(pk=form.cleaned_data["element2"].id).delete()

                messages.success(request, "Fusion r??ussie entre les deux " + pluriel + " " + form.cleaned_data["element1"].nom + " et " + form.cleaned_data["element2"].nom)
                return HttpResponseRedirect(reverse(reverse_url_main))
    else:
        form = classform()

    return render(request, "fiches/merge.html", {
        'titre': "Fusion de deux " + pluriel,
        'form': form,
        'pluriel': pluriel
    })
