from django.http import HttpResponse
from django.template import loader
from .models import Fiche, Niveau, Categorie, Auteur, CategorieLibre, Theme, MotCle, EntreeGlossaire
from django.shortcuts import get_object_or_404, render
from .forms import FicheForm
from django.db.models import Count, Q, Case, When, IntegerField

from django.views.generic import DetailView

from django_weasyprint import WeasyTemplateResponseMixin
from django_weasyprint.views import WeasyTemplateResponse

from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin


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

    nbmotcles = 15
    motcles = MotCle.objects.annotate(fiche_count=Count('fiche')).order_by("-fiche_count", "nom")[:nbmotcles]
    nbmotcles = motcles.count()

    nbcategorieslibres = 9
    categories_libres = CategorieLibre.objects.annotate(fiche_count=Count('fiche')).order_by("-fiche_count", "nom")[:nbcategorieslibres]
    nbcategorieslibres = categories_libres.count()

    context = {'fiche_list': latest_fiche_list, 'nbfiches': nbfiches,
               "nbfichestotal": Fiche.objects.count(), "niveaux": niveaux,
               "categories": categories, "nbcategories": nbcategories,
               "auteurs": auteurs,
               "themes": themes, "nbthemes": nbthemes,
               "motcles": motcles, "nbmotcles": nbmotcles,
               "categories_libres": categories_libres, "nbcategorieslibres": nbcategorieslibres,
               "nbentreesglossaire": nbentreesglossaire
               }
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
    return render(request, 'fiches/detail.html', {'fiche': fiche})


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


@login_required
def categories(request):
    categories = Categorie.objects.filter().annotate(fiche_count=Count(Case(When(Q(fiche_categorie1__isnull=False) | Q(fiche_categorie2__isnull=False) | Q(fiche_categorie3__isnull=False), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.A) | Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.A) | Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.B) | Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.B) | Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.C) | Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.C) | Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                   "elements": categories, "titre": "Toutes les catégories", "nom_humain": "catégorie",
                                                   "visu_code": "basic", "visu": "triées par nombre total de fiches"})


@login_required
def categories_alpha(request):
    categories = Categorie.objects.filter().annotate(fiche_count=Count(Case(When(Q(fiche_categorie1__isnull=False) | Q(fiche_categorie2__isnull=False) | Q(fiche_categorie3__isnull=False), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.A) | Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.A) | Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.B) | Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.B) | Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche_categorie1__niveau__applicable=Niveau.Applicabilite.C) | Q(fiche_categorie2__niveau__applicable=Niveau.Applicabilite.C) | Q(fiche_categorie3__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("code")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories", "critere_name": "categorie",
                                                   "elements": categories, "titre": "Toutes les catégories", "nom_humain": "catégorie",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


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


@login_required
def categories_libres(request):
    categories_libres = CategorieLibre.objects.filter().annotate(fiche_count=Count('fiche')). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories_libres", "critere_name": "categorie_libre",
                                                   "elements": categories_libres, "titre": "Toutes les catégories libres", "nom_humain": "catégorie libre",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches"})


@login_required
def categories_libres_alpha(request):
    categories_libres = CategorieLibre.objects.filter().annotate(fiche_count=Count('fiche')). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("nom")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "categories_libres", "critere_name": "categorie_libre",
                                                   "elements": categories_libres, "titre": "Toutes les catégories libres", "nom_humain": "catégorie libre",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


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
    themes = Theme.objects.filter().annotate(fiche_count=Count('fiche')). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les thèmes", "nom_humain": "thème",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches"})


@login_required
def themes_alpha(request):
    themes = Theme.objects.filter().annotate(fiche_count=Count('fiche')). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("nom")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "themes", "critere_name": "theme",
                                                   "elements": themes, "titre": "Tous les thèmes", "nom_humain": "thème",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


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
    motscles = MotCle.objects.filter().annotate(fiche_count=Count('fiche')). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("-fiche_count")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                   "elements": motscles, "titre": "Tous les mots-clés", "nom_humain": "mot-clé",
                                                   "visu_code": "basic", "visu": "triées par nombre de fiches"})


@login_required
def motscles_alpha(request):
    motscles = MotCle.objects.filter().annotate(fiche_count=Count('fiche')). \
        annotate(fiche_count_A=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.A), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_B=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.B), then=1), output_field=IntegerField(),))). \
        annotate(fiche_count_C=Count(Case(When(Q(fiche__niveau__applicable=Niveau.Applicabilite.C), then=1), output_field=IntegerField(),))). \
        order_by("nom")
    return render(request, 'fiches/critere.html', {"critere_name_pluriel": "motscles", "critere_name": "motcle",
                                                   "elements": motscles, "titre": "Tous les mots-clés", "nom_humain": "mot-clé",
                                                   "visu_code": "alpha", "visu": "par ordre alphabétique"})


@login_required
def rechercher(request):

    results = None
    recherche = None

    if request.method == "GET":
        recherche = request.GET.get('search')
        if recherche != '':
            results = Fiche.rechercher(recherche)

    return render(request, 'fiches/rechercher.html', {'results': results, 'recherche': recherche})


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


class FicheViewPDF(LoginRequiredMixin, WeasyTemplateResponseMixin, DetailView):

    template_name = 'fiches/detail_pdf.html'

    model = Fiche

    def get_pdf_filename(self):
        from django.utils import timezone
        return '{nom} {at}.pdf'.format(
            nom=str(self.get_object()),
            at=str(self.get_object().date_derniere_modification.strftime("%d-%m-%Y %H:%M:%S")),
        )
