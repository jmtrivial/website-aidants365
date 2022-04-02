from django.http import HttpResponse
from django.template import loader
from .models import Fiche, Niveau, Categorie, Auteur, CategorieLibre, Theme, MotCle, EntreeGlossaire, EntreeAgenda
from django.shortcuts import get_object_or_404, render
from .forms import FicheForm
from django.db.models import Count, Q, Case, When, IntegerField, Max, F, ExpressionWrapper, Value
from decimal import Decimal
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.http import Http404

from django.views.generic import DetailView

from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import WeasyTemplateResponse

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import Agenda, Ephemeride, table, arrayToString


def annoter_class_nuage(objects):
    nb_max = 5
    nb = objects.aggregate(Max("fiche_count"))["fiche_count__max"]
    return objects.annotate(classe_nuage=ExpressionWrapper(F('fiche_count') * Decimal(nb_max) / Decimal(nb), output_field=IntegerField())). \
        annotate(max_classe_nuage=Value(nb_max))


@login_required
def accueil(request):
    nbfiches = 5
    latest_fiche_list = Fiche.objects.order_by('-date_derniere_modification')[:5]
    nbfiches = latest_fiche_list.count()

    nbentreesglossaire = EntreeGlossaire.objects.count()

    niveaux = Niveau.objects.annotate(fiche_count=Count('fiche')).order_by("ordre")

    nbcategories = 9
    categories = Categorie.objects.annotate(fiche_count=Count(Case(When(Q(fiche_categorie1__isnull=False) | Q(fiche_categorie2__isnull=False) | Q(fiche_categorie3__isnull=False), then=1), output_field=IntegerField(),)))[:nbcategories]
    nbcategories = categories.count()

    auteurs = Auteur.objects.annotate(fiche_count=Count('fiche'))

    nbthemes = 15
    themes = Theme.objects.annotate(fiche_count=Count('fiche')).order_by("-fiche_count", "nom")[:nbthemes]
    nbthemes = themes.count()

    motcles = MotCle.objects.annotate(fiche_count=Count('fiche')).order_by("nom")
    motcles = annoter_class_nuage(motcles)

    nbcategorieslibres = 9
    categories_libres = CategorieLibre.objects.annotate(fiche_count=Count('fiche')).order_by("-fiche_count", "nom")[:nbcategorieslibres]
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
                                                             "critere_human": "du catégorie", "critere_nom": str(categorie),
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
        annotate(fiche_count=F("fiche_count1") + F("fiche_count2") + F("fiche_count3"))


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
                                                   "visu_code": "basic", "visu": "triées par nombre total de fiches"})


@login_required
def categories_alpha(request):
    categories = annotate_categories_par_niveau_complet().order_by("-fiche_count").order_by("code")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                   "elements": categories, "titre": "Toutes les catégories",
                                                   "nom_humain": "catégorie", "nom_humain_pluriel": "catégorie",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


@login_required
def categories_nuage(request):
    categories = annotate_categories_par_niveau().order_by("code")
    categories = annoter_class_nuage(categories)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                         "elements": categories, "titre": "Toutes les catégories",
                                                         "nom_humain": "catégorie", "nom_humain_pluriel": "catégories"})


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
                                                             "critere_human": "de la catégorie libre", "critere_nom": str(categorie_libre),
                                                             "fiche_list": fiches})


@login_required
def index_categorie_libre_detail(request, id1, id2):
    categorie_libre = get_object_or_404(CategorieLibre, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(categories_libres=categorie_libre)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "categorie_libre", "critere": categorie_libre,
                                                                    "critere_human": "de la catégorie libre", "critere_nom": str(categorie_libre),
                                                                    "fiche_list": fiches, "fiche": fiche})


def annotate_categories_par_niveau_simple(objects):
    return objects.annotate(fiche_count=Count('fiche', distinct=True)). \
        annotate(fiche_count_A=Count('fiche', filter=Q(fiche__niveau__applicable=Niveau.Applicabilite.A), distinct=True)). \
        annotate(fiche_count_B=Count('fiche', filter=Q(fiche__niveau__applicable=Niveau.Applicabilite.B), distinct=True)). \
        annotate(fiche_count_C=Count('fiche', filter=Q(fiche__niveau__applicable=Niveau.Applicabilite.C), distinct=True))


@login_required
def categories_libres(request):
    categories_libres = annotate_categories_par_niveau_simple(CategorieLibre.objects).order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories_libres", "critere_name": "categorie_libre",
                                                   "elements": categories_libres, "titre": "Toutes les catégories libres",
                                                   "nom_humain": "catégorie libre", "nom_humain_pluriel": "catégories libres",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches"})


@login_required
def categories_libres_alpha(request):
    categories_libres = annotate_categories_par_niveau_simple(CategorieLibre.objects).order_by("nom")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories_libres", "critere_name": "categorie_libre",
                                                   "elements": categories_libres, "titre": "Toutes les catégories libres",
                                                   "nom_humain": "catégorie libre", "nom_humain_pluriel": "catégories libres",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


@login_required
def categories_libres_nuage(request):
    categories_libres = CategorieLibre.objects.filter().annotate(fiche_count=Count('fiche', distinct=True)). \
        order_by("nom")
    categories_libres = annoter_class_nuage(categories_libres)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "categories_libres", "critere_name": "categorie_libre",
                                                         "elements": categories_libres, "titre": "Toutes les catégories libres", "nom_humain": "catégorie libre"})


@login_required
def index_theme(request, id):
    theme = get_object_or_404(Theme, pk=id)
    fiches = Fiche.objects.filter(themes=theme)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "theme", "critere": theme,
                                                             "critere_human": "du thème",
                                                             "critere_nom": str(theme), "fiche_list": fiches})


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
    themes = annotate_categories_par_niveau_simple(Theme.objects).order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les thèmes",
                                                   "nom_humain": "thème", "nom_humain_pluriel": "thèmes",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches"})


@login_required
def themes_alpha(request):
    themes = annotate_categories_par_niveau_simple(Theme.objects).order_by("nom")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les thèmes",
                                                   "nom_humain": "thème", "nom_humain_pluriel": "thèmes",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


@login_required
def themes_nuage(request):
    themes = Theme.objects.filter().annotate(fiche_count=Count('fiche', distinct=True)). \
        order_by("nom")
    themes = annoter_class_nuage(themes)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                         "elements": themes, "titre": "Tous les thèmes",
                                                         "nom_humain": "thème", "nom_humain_pluriel": "thèmes"})


@login_required
def index_motcle(request, id):
    motcle = get_object_or_404(MotCle, pk=id)
    fiches = Fiche.objects.filter(mots_cles=motcle)
    return render(request, 'fiches/index_par_critere.html', {"critere_name": "motcle", "critere": motcle,
                                                             "critere_human": "du mot-clé", "critere_nom": str(motcle),
                                                             "fiche_list": fiches})


@login_required
def index_motcle_detail(request, id1, id2):
    motcle = get_object_or_404(MotCle, pk=id1)
    fiche = get_object_or_404(Fiche, pk=id2)
    fiches = Fiche.objects.filter(mots_cles=motcle)
    return render(request, 'fiches/index_par_critere_detail.html', {"critere_name": "motcle", "critere": motcle,
                                                                    "critere_human": "du mot-clé", "critere_nom": str(motcle),
                                                                    "fiche_list": fiches, "fiche": fiche})


@login_required
def motscles(request):
    motscles = annotate_categories_par_niveau_simple(MotCle.objects).order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                   "elements": motscles, "titre": "Tous les mots-clés",
                                                   "nom_humain": "mot-clé", "nom_humain_pluriel": "mots-clés",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches"})


@login_required
def motscles_alpha(request):
    motscles = annotate_categories_par_niveau_simple(MotCle.objects).order_by("nom")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                   "elements": motscles, "titre": "Tous les mots-clés",
                                                   "nom_humain": "mot-clé", "nom_humain_pluriel": "mots-clés",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


@login_required
def motscles_nuage(request):
    motscles = MotCle.objects.filter().annotate(fiche_count=Count('fiche', distinct=True)).order_by("nom")
    motscles = annoter_class_nuage(motscles)
    return render(request, 'fiches/critere_nuage.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                         "elements": motscles, "titre": "Tous les mots-clés",
                                                         "nom_humain": "mot-clé", "nom_humain_pluriel": "mots-clés"})


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

    return render(request, 'fiches/rechercher.html', {'results_fiches': results_fiches,
                                                      'results_glossaire': results_glossaire,
                                                      'results_agenda': results_agenda,
                                                      'recherche': recherche})


@login_required
def glossaire(request):
    entrees = EntreeGlossaire.objects.order_by('entree')
    context = {'entrees': entrees}
    return render(request, 'fiches/index_entree_glossaire.html', context)


@login_required
def entree_glossaire(request, id):
    entree = get_object_or_404(EntreeGlossaire, pk=id)
    context = {'entree': entree}
    return render(request, 'fiches/entree_glossaire.html', context)


@login_required
def agenda(request):
    entrees = EntreeAgenda.objects
    aa = Agenda(entrees, 0, 'fr_FR.UTF-8')
    context = {'agenda': aa}
    return render(request, 'fiches/agenda.html', context)


@login_required
def entree_agenda(request, id):
    entree = get_object_or_404(EntreeAgenda, pk=id)
    context = {'entree': entree}
    return render(request, 'fiches/entree_agenda.html', context)


class FicheViewPDF(LoginRequiredMixin, WeasyTemplateResponseMixin, DetailView):

    template_name = 'fiches/detail_pdf.html'

    model = Fiche

    def get_pdf_filename(self):
        from django.utils import timezone
        return '{nom} {at}.pdf'.format(
            nom=str(self.get_object()),
            at=str(self.get_object().date_derniere_modification.strftime("%d-%m-%Y %H:%M:%S")),
        )


def page_not_found_view(request, exception=None):
    return render(request, 'fiches/404.html', {"exception": exception})
