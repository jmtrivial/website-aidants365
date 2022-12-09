from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models.signals import pre_save, post_init
from django.db.models import Func, F, Value, Q
from django.db.models.functions import Concat, Right
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User
from django_better_admin_arrayfield.models.fields import ArrayField
import re
from django.utils.html import strip_tags
from django.utils.text import Truncator
from .utils import table, arrayToString, Agenda
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from django.contrib.postgres.aggregates.general import ArrayAgg
from sortedm2m.fields import SortedManyToManyField
from .utils import message_glossaire, message_sortable
import locale
from datetime import date, timedelta
from django.utils.translation import gettext as _


import logging
logger = logging.getLogger(__name__)


def build_list_urls(txt):
    return sorted(list(set([x[1] for x in re.findall(r"(^|\<p\>|[\n \"])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", txt)])))


def rechercher_nom_simple(search_text, classname):
    from django.contrib.postgres.search import SearchVector
    from django.contrib.postgres.search import SearchQuery

    if not search_text:
        return None

    search_vectors = SearchVector('nom', weight='A', config='french')
    search_query = SearchQuery(search_text, config='french')
    return classname.objects.annotate(search=search_vectors).filter(search=search_query). \
        annotate(nom_hl=SearchHeadline("nom",
                 search_query,
                 start_sel="<span class=\"highlight\">",
                 stop_sel="</span>",
                 max_fragments=50,
                 config='french'))


class EntetePage(models.Model):

    page = models.CharField(unique=True, max_length=32)
    texte = RichTextField(verbose_name="Texte de l'entête", config_name='main_ckeditor', blank=True)

    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    def save(self, *args, **kwargs):
        self.date_derniere_modification = timezone.now()
        super().save(*args, **kwargs)

    def url_name(self):
        return EntetePage.page_url_name(self.page)

    def url_parameters(self):
        return EntetePage.page_url_parameters(self.page)

    def get_absolute_url(self):
        return reverse(self.url_name(), args=self.url_parameters())

    def page_url_name(page_name):
        if page_name.startswith("agenda/"):
            return "fichier:agenda_month"
        elif page_name.startswith("agenda"):
            return "fichier:agenda"
        else:
            return "fichier:" + page_name

    def page_url_parameters(page_name):
        if page_name.startswith("agenda/"):
            return [int(x) for x in page_name.split("/")[1:3]]
        else:
            return []

    def edit_url(self):
        return reverse("fichier:object_change", kwargs={'classname': 'entete_page', 'id': self.pk})

    def create_url(page_name):
        return reverse("fichier:object_add", kwargs={'classname': 'entete_page'}) + "?page=" + page_name

    def get_nom_page(self):
        return EntetePage.nom_page(self.page)

    def nom_page(page):
        if page.startswith("agenda/") or page.startswith("agenda:"):
            elements = page.split("/")
            if len(elements) == 1:
                elements = page.split(":")
            mois = Agenda.month_name[int(elements[2])]
            annee = elements[1]
            if mois[0] in ['a', 'e', 'i', 'o', 'u']:
                return "du mois d'" + mois + " " + annee
            else:
                return "du mois de " + mois + " " + annee
        else:
            nom_page = {"index": "des fiches", "desk": "du desk", "categories": "des catégories",
                        "glossaire": "du glossaire", "accueil": "de l'accueil",
                        "themes": "des thèmes", "etiquettes": "des étiquettes", "agenda": "de l'agenda",
                        "liens_sortants": "des liens sortants"}
            return nom_page[page]

    def __str__(self):
        return "la page " + EntetePage.nom_page(self.page)

    def rechercher(search_text):
        from django.contrib.postgres.search import SearchVector
        from django.contrib.postgres.search import SearchQuery

        if not search_text:
            return None

        search_vectors = SearchVector('texte', weight='A', config='french')
        search_query = SearchQuery(search_text, config='french')
        return EntetePage.objects.annotate(search=search_vectors).filter(search=search_query). \
            annotate(texte_hl=SearchHeadline("texte",
                     search_query,
                     start_sel="<span class=\"highlight\">",
                     stop_sel="</span>",
                     max_fragments=50,
                     config='french'))


class Niveau(models.Model):

    class Applicabilite(models.TextChoices):
        A = 'A', "informatif"
        B = 'B', "pratique"
        C = 'C', "opérationnel"

        def couleur(appl):
            if appl == Niveau.Applicabilite.A:
                return Niveau.couleur_A
            elif appl == Niveau.Applicabilite.B:
                return Niveau.couleur_B
            else:
                return Niveau.couleur_C

        def nom(appl):
            if appl == Niveau.Applicabilite.A:
                return Niveau.Applicabilite.A.label
            elif appl == Niveau.Applicabilite.B:
                return Niveau.Applicabilite.B.label
            else:
                return Niveau.Applicabilite.C.label

    couleur_A = "#fdfbe9"
    couleur_B = "#ea841d"
    couleur_C = "#67b43f"

    ordre = models.IntegerField(verbose_name="Numéro", unique=True)
    code = models.CharField(verbose_name="Code", max_length=4, unique=True)
    nom = models.CharField(verbose_name="Nom", max_length=64)
    description = models.CharField(verbose_name="Description", max_length=256, blank=True, null=True)
    applicable = models.CharField(max_length=1, choices=Applicabilite.choices, default=Applicabilite.B)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    def delete(self, *args, **kwargs):
        self.update_associated_entries()
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()
        self.date_derniere_modification = timezone.now()
        super().save(*args, **kwargs)

    def couleur(self):
        return Niveau.Applicabilite.couleur(self.applicable)

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"

    def __str__(self):
        return " ".join(["{:02d}".format(self.ordre), self.code])

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, Niveau)

    def associated_entries(self):
        result = []

        # Liste des entrées d'agenda associées à cette catégorie
        result += Fiche.objects.filter(themes=self.id)

        return result

    def update_associated_entries(self):
        for e in self.associated_entries():
            e.date_demande_mise_a_jour = timezone.now()
            e.save()


class TypeCategorie(models.Model):
    nom = models.CharField(verbose_name="Nom du type de catégorie", max_length=64, unique=True)

    class Meta:
        verbose_name = "Type de catégorie"
        verbose_name_plural = "Types de catégorie"

    def __str__(self):
        return self.nom

    def description_longue(self):
        return self.nom


class Categorie(models.Model):
    code = models.CharField(verbose_name="Code de la catégorie", max_length=4, unique=True)
    nom = models.CharField(verbose_name="Nom de la catégorie", max_length=64)
    type_categorie = models.ForeignKey(TypeCategorie, verbose_name="Type de la catégorie", on_delete=models.SET_NULL, blank=True, null=True)
    is_biblio = models.BooleanField(verbose_name="Nécessite les champs de bibliographie", default=False)
    is_site = models.BooleanField(verbose_name="Nécessite les champs de site internet", default=False)
    is_film = models.BooleanField(verbose_name="Nécessite les champs d'un film", default=False)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.code

    def get_absolute_url(self):
        return reverse('fichier:index_categorie', kwargs={'id': self.pk})

    def description_longue(self):
        return self.code + " — " + self.nom

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, Categorie)

    def delete(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()
        self.date_derniere_modification = timezone.now()
        super().save(*args, **kwargs)

    def associated_entries(self):
        result = []

        # Liste des entrées d'agenda associées à cette catégorie
        result += Fiche.objects.filter(Q(categorie1=self.id) | Q(categorie2=self.id) | Q(categorie3=self.id))

        return result

    def update_associated_entries(self):
        for e in self.associated_entries():
            e.date_demande_mise_a_jour = timezone.now()
            e.save()


class Auteur(models.Model):
    code = models.CharField(verbose_name="Code auteur", max_length=3)
    nom = models.CharField(verbose_name="Nom complet", max_length=64)
    compte = models.ForeignKey(User, verbose_name="Compte utilisateur correspondant", on_delete=models.SET_NULL, blank=True, null=True)

    def get_connected_auteur(user):
        result = Auteur.objects.filter(compte=user)
        if not result:
            return None
        else:
            return result[0]

    class Meta:
        verbose_name = "Auteur"
        verbose_name_plural = "Auteurs"

    def __str__(self):
        return self.code


class Etiquette(models.Model):
    nom = models.CharField(verbose_name="Étiquette", max_length=64, unique=True, blank=False)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Étiquette"
        verbose_name_plural = "Étiquettes"

    def __str__(self):
        return self.nom

    def delete(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()
        self.date_derniere_modification = timezone.now()
        super().save(*args, **kwargs)

    def description_longue(self):
        return self.nom

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, Etiquette)

    def associated_entries(self):
        result = []
        # Liste des fiches ayant cette étiquette
        result += Fiche.objects.filter(etiquettes=self.id)

        # Liste des entrées d'agenda ayant cette étiquette
        result += EntreeAgenda.objects.filter(etiquettes=self.id)

        return result

    def update_associated_entries(self):
        for e in self.associated_entries():
            e.date_demande_mise_a_jour = timezone.now()
            e.save()

    def get_absolute_url(self):
        return reverse('fichier:index_etiquette', kwargs={'id': self.pk})


class Theme(models.Model):
    nom = models.CharField(verbose_name="Thème", max_length=64, unique=True, blank=False)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    class Meta:
        verbose_name = "Thème"
        verbose_name_plural = "Thèmes"

    def __str__(self):
        return self.nom

    def delete(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()

        self.date_derniere_modification = timezone.now()
        super().save(*args, **kwargs)

    def description_longue(self):
        return self.nom

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, Theme)

    def associated_entries(self):
        result = []
        # Liste des fiches ayant ce theme
        result += Fiche.objects.filter(themes=self.id)

        # Liste des entrées d'agenda ayant ce thème
        result += EntreeAgenda.objects.filter(themes=self.id)

        return result

    def update_associated_entries(self):
        for e in self.associated_entries():
            e.date_demande_mise_a_jour = timezone.now()
            e.save()

    def get_absolute_url(self):
        return reverse('fichier:index_theme', kwargs={'id': self.pk})


class Fiche(models.Model):
    # entête

    niveau = models.ForeignKey(Niveau, verbose_name="Niveau", on_delete=models.RESTRICT)
    categorie1 = models.ForeignKey(Categorie, verbose_name="Catégorie principale", on_delete=models.RESTRICT, related_name='%(class)s_categorie1')
    categorie2 = models.ForeignKey(Categorie, verbose_name="Deuxième catégorie", on_delete=models.SET_NULL, related_name='%(class)s_categorie2', blank=True, null=True)
    categorie3 = models.ForeignKey(Categorie, verbose_name="Troisième catégorie", on_delete=models.SET_NULL, related_name='%(class)s_categorie3', blank=True, null=True)

    auteur = models.ForeignKey(Auteur, verbose_name="Auteur", on_delete=models.RESTRICT)
    marque = models.BooleanField(verbose_name="Entrée de qualité", default=False)

    numero = models.IntegerField(verbose_name="Numéro", default=9999)
    titre_fiche = models.CharField(verbose_name="Titre de la fiche", max_length=256)
    sous_titre = models.CharField(verbose_name="Sous-titre", max_length=256, blank=True)

    date_creation = models.DateField(verbose_name="Date de création", default=timezone.now)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)
    date_demande_mise_a_jour = models.DateTimeField(verbose_name="Demande de mise à jour", auto_now=True)

    # chapeau
    url = models.URLField(verbose_name="Adresse", max_length=1024, blank=True)

    # uniquement si biblio
    titre = models.CharField(verbose_name="Titre de l'ouvrage", max_length=1024, blank=True)
    auteurs = models.CharField(verbose_name="Auteur(s)", max_length=1024, blank=True)
    annee_publication = models.IntegerField(verbose_name="Année de publication", blank=True, null=True)
    editeur = models.CharField(verbose_name="Éditeur", max_length=1024, blank=True)
    collection = models.CharField(verbose_name="Collection", max_length=1024, blank=True)
    format_bibl = models.CharField(verbose_name="Format", max_length=1024, blank=True, help_text="Format attendu: ??.? x ??.? cm, ?? pages")

    # uniquement si film
    realisateurs = models.CharField(verbose_name="Réalisateur(s)", max_length=1024, blank=True)
    acteurs = models.CharField(verbose_name="Acteur(s)", max_length=1024, blank=True)
    annee_film = models.IntegerField(verbose_name="Année de production", blank=True, null=True)
    diffusion = models.CharField(verbose_name="Diffusion", max_length=1024, blank=True, null=True)
    duree = models.CharField(verbose_name="Durée", max_length=32, blank=True)
    production = models.CharField(verbose_name="Production", max_length=1024, blank=True)

    # uniquement si site
    partenaires = models.CharField(verbose_name="Partenaires", max_length=1024, blank=True, null=True)

    themes = SortedManyToManyField(Theme, verbose_name="Thèmes", blank=True, help_text=message_sortable)
    etiquettes = SortedManyToManyField(Etiquette, verbose_name="Étiquettes", blank=True, help_text=message_sortable)

    # corps
    presentation = RichTextField(verbose_name="Présentation", config_name='main_ckeditor', blank=True, help_text=message_glossaire)

    problematique = RichTextField(verbose_name="Problématique", config_name='main_ckeditor', blank=True, help_text=message_glossaire)

    # uniquement si biblio
    quatrieme_de_couverture = RichTextField(verbose_name="Quatrième de couverture", config_name='main_ckeditor', blank=True, help_text=message_glossaire)

    # uniquement si site
    plan_du_site = RichTextField(verbose_name="Plan du site", config_name='main_ckeditor', blank=True, help_text=message_glossaire)

    detail_focus = models.CharField(verbose_name="Détail du focus (placé après le mot \"Focus\")", max_length=1024, blank=True)

    focus = RichTextField(verbose_name="Focus", config_name='main_ckeditor', blank=True, help_text=message_glossaire)

    # pied de page
    reserves = RichTextField(verbose_name="Réserves", config_name='main_ckeditor', blank=True, help_text=message_glossaire)
    lesplus = RichTextField(verbose_name="Les plus", config_name='main_ckeditor', blank=True, help_text=message_glossaire)
    en_savoir_plus = RichTextField(verbose_name="En savoir plus", config_name='main_ckeditor', blank=True, help_text=message_glossaire)
    fiches_connexes = SortedManyToManyField("self", verbose_name="Fiches connexes", blank=True, help_text=message_sortable)

    # url (extraites automatiquement au moment de publier)
    urls = ArrayField(models.URLField(verbose_name="Adresse", max_length=1024, blank=True), blank=True, null=True)

    class Meta:
        verbose_name = "Fiche"
        verbose_name_plural = "Fiches"
        ordering = ["auteur", "numero"]

    def get_descriptions(self):
        return [self.presentation, self.problematique, self.quatrieme_de_couverture,
                self.plan_du_site, self.focus,
                self.reserves, self.lesplus, self.en_savoir_plus]

    def get_simple_name(self):
        liste = [self.niveau, self.categorie1, self.auteur, "{:04d}".format(self.numero), self.titre_fiche]
        return " ".join(map(str, liste))

    def __str__(self):
        name = self.get_simple_name()
        if self.marque:
            name += " ☑"
        return name

    def delete(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()

        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # update associated entries
        self.update_associated_entries()
        self.date_derniere_modification = timezone.now()
        self.urls = build_list_urls(self.url + " " + self.presentation + " " + self.problematique + " " + self.quatrieme_de_couverture + " " + self.plan_du_site + " " + self.focus + " " + self.reserves + " " + self.lesplus + " " + self.en_savoir_plus)
        super().save(*args, **kwargs)

    def get_numero_suivant(auteur):
        if Fiche.objects.all().count() == 0:
            nouveau_numero = 1
        else:
            nouveau_numero = Fiche.objects.all().filter(auteur=auteur).exclude(numero=9999).aggregate(models.Max('numero'))['numero__max']
            if nouveau_numero is None:
                nouveau_numero = 1
            else:
                nouveau_numero += 1
        return nouveau_numero

    def get_absolute_url(self):
        return reverse('fichier:detail', kwargs={'id': self.pk})

    def rechercher(search_text):
        from django.contrib.postgres.search import SearchVector
        from django.contrib.postgres.search import SearchQuery

        if not search_text:
            return None

        search_vectors = SearchVector('agg_title', weight='B', config='french') + SearchVector('agg_contenu', weight='A', config='french')
        search_query = SearchQuery(search_text, config='french')

        return Fiche.objects.annotate(agg_title=Concat(Right(Concat(Value("00"), "niveau__ordre"), 2), Value(" "), "niveau__code", Value(" "),
                                                       "categorie1__code", Value(" "), "auteur__code", Value(" "),
                                                       Right(Concat(Value("0000"), "numero"), 4), Value(" "), "titre_fiche", output_field=models.CharField())). \
            annotate(agg_contenu=Concat("sous_titre", Value(" "),
                                        "themes__nom", Value(" "), "etiquettes__nom", Value(" "),
                                        "presentation", Value(" "), "problematique", Value(" "), "quatrieme_de_couverture", Value(" "),
                                        "plan_du_site", Value(" Focus "), "detail_focus", Value(" "), "focus", Value(" "), "titre", Value(" "), "editeur", Value(" "), "auteurs", Value(" "), "collection",
                                        "partenaires", Value(" "), "reserves", Value(" "), "lesplus", Value(" "), "en_savoir_plus", output_field=models.CharField())).order_by("id").distinct('id'). \
            annotate(search=search_vectors).filter(search=search_query). \
            annotate(agg_title_hl=SearchHeadline("agg_title", search_query,
                     start_sel="<span class=\"highlight\">",
                     stop_sel="</span>",
                     highlight_all=True,
                     config='french')). \
            annotate(agg_contenu_hl=SearchHeadline("agg_contenu", search_query,
                     start_sel="<span class=\"highlight\">",
                     stop_sel="</span>",
                     max_fragments=50,
                     config='french'))

    def associated_entries(self):
        result = []

        # Liste des entrées d'agenda associées à cette fiche
        result += EntreeAgenda.objects.filter(fiches_associees=self.id)

        return result

    def update_associated_entries(self):
        for e in self.associated_entries():
            e.date_demande_mise_a_jour = timezone.now()
            e.save()


class EntreeGlossaire(models.Model):

    class Meta:
        verbose_name = "Entrée du glossaire"
        verbose_name_plural = "Entrées du glossaire"

    def __str__(self):
        return self.entree

    entree = models.CharField(verbose_name="Entrée", max_length=128, unique=False, blank=False)
    formes_alternatives = ArrayField(models.CharField(max_length=128, blank=True), verbose_name="Signification et formes alternatives", blank=True, null=True)

    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    definition = RichTextField(verbose_name="Définition", config_name='main_ckeditor', blank=True)

    # url (extraites automatiquement au moment de publier)
    urls = ArrayField(models.URLField(verbose_name="Adresse", max_length=1024, blank=True), blank=True, null=True)

    def get_absolute_url(self):
        return reverse('fichier:entree_glossaire', kwargs={'id': self.pk})

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.date_derniere_modification = timezone.now()
        self.urls = build_list_urls(self.definition)
        super().save(*args, **kwargs)

    def matching_entrees_agenda(self):
        result = []

        for e in EntreeAgenda.objects.filter():
            if re.search(r'\[%s\]' % self.entree, str(e.notes), flags=re.I):
                result.append(e)
                break
            else:
                found = False
                if self.formes_alternatives:
                    for fa in self.formes_alternatives:
                        if re.search(r'\[%s\]' % fa, str(e.notes), flags=re.I):
                            result.append(e)
                            found = True
                            break
                    if found:
                        break

        return result

    def matching_fiches(self):
        result = []

        for f in Fiche.objects.filter():
            for t in f.get_descriptions():
                if re.search(r'\[%s\]' % self.entree, str(t), flags=re.I):
                    result.append(f)
                    break
                else:
                    found = False
                    if self.formes_alternatives:
                        for fa in self.formes_alternatives:
                            if re.search(r'\[%s\]' % fa, str(t), flags=re.I):
                                result.append(f)
                                found = True
                                break
                        if found:
                            break

        return result

    def rechercher(search_text):

        if not search_text:
            return None

        search_vectors = SearchVector('definition', weight='A', config='french') + \
            SearchVector('entree', weight='B', config='french') + \
            SearchVector('formes_alternatives', weight='C', config='french')
        search_query = SearchQuery(search_text, config='french')

        return EntreeGlossaire.objects.annotate(tt=arrayToString("formes_alternatives")). \
            annotate(search=search_vectors).filter(search=search_query). \
            annotate(definition_hl=SearchHeadline("definition",
                                                  search_query,
                                                  start_sel="<span class=\"highlight\">",
                                                  stop_sel="</span>",
                                                  max_fragments=50,
                                                  config='french'),
                     entree_hl=SearchHeadline("entree",
                                              search_query,
                                              start_sel="<span class=\"highlight\">",
                                              stop_sel="</span>",
                                              highlight_all=True,
                                              config='french'),
                     formes_alternatives_hl=SearchHeadline("tt",
                                                           search_query,
                                                           start_sel="<span class=\"highlight\">",
                                                           stop_sel="</span>",
                                                           highlight_all=True,
                                                           config='french'))

    def associated_entries(self):
        # Liste des entrées d'agenda et les fiches associées à cette entrée de glossaire
        return self.matching_entrees_agenda() + self.matching_fiches()


class EntreeAgenda(models.Model):

    class Meta:
        verbose_name = "Entrée de l'agenda"
        verbose_name_plural = "Entrées de l'agenda"

    date = models.DateField(blank=True, null=True)

    marque = models.BooleanField(verbose_name="Entrée de qualité", default=False)
    niveau = models.ForeignKey(Niveau, verbose_name="Niveau dominant du contenu", on_delete=models.RESTRICT, blank=True, null=True)

    themes = SortedManyToManyField(Theme, verbose_name="Thèmes associés", blank=True, help_text=message_sortable)
    etiquettes = SortedManyToManyField(Etiquette, verbose_name="Étiquettes associées", blank=True, help_text=message_sortable)

    notes = RichTextField(verbose_name="Notes", config_name='main_ckeditor', blank=True, help_text=message_glossaire)

    illustration = models.ImageField(verbose_name="Illustration", upload_to='illustrations_agenda', blank=True, null=True)

    illustration_alt = models.CharField(verbose_name="Texte alternatif à l'illustration (audiodescription)", max_length=512, default="", blank=True, null=True)

    illustration_source = models.CharField(verbose_name="Source de l'illustration", max_length=512, default="", blank=True, null=True)

    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)
    date_demande_mise_a_jour = models.DateTimeField(verbose_name="Demande de mise à jour", auto_now=True)

    fiches_associees = SortedManyToManyField(Fiche, verbose_name="Fiches associées", blank=True, help_text=message_sortable)

    # url (extraites automatiquement au moment de publier)
    urls = ArrayField(models.URLField(verbose_name="Adresse", max_length=1024, blank=True), blank=True, null=True)

    def get_absolute_url(self):
        return reverse('fichier:entree_agenda', kwargs={'year': self.date.year, 'month': self.date.month, 'day': self.date.day})

    def __str__(self):
        texte = self.date.strftime("%d/%m/%Y")
        if self.marque:
            return texte + " ☑"
        else:
            return texte

    def save(self, *args, **kwargs):
        self.date_derniere_modification = timezone.now()
        self.urls = build_list_urls(self.notes)
        super().save(*args, **kwargs)

    def iso(self):
        return self.date.strftime("%Y-%m-%d")

    def ephemeride(self):
        e = Ephemeride(self.date, self.get_absolute_url(), False)
        return e.ephemeride()

    def to_ephemeride(self):
        return Ephemeride(self)

    def date_complete(self):
        return Agenda.day_name[self.date.weekday()] + " " + str(self.date.day) + " " + Agenda.month_name[self.date.month] + " " + str(self.date.year)

    def rechercher(search_text):
        from django.contrib.postgres.search import SearchVector
        from django.contrib.postgres.search import SearchQuery

        if not search_text:
            return None

        search_vectors = SearchVector('agg_contenu', weight='A', config='french')
        search_query = SearchQuery(search_text, config='french')

        return EntreeAgenda.objects. \
            annotate(agg_contenu=Concat("themes__nom", Value(" "), "etiquettes__nom", Value(" "), "notes", output_field=models.CharField())).order_by("id").distinct('id'). \
            annotate(search=search_vectors).filter(search=search_query). \
            annotate(notes_hl=SearchHeadline("agg_contenu",
                     search_query,
                     start_sel="<span class=\"highlight\">",
                     stop_sel="</span>",
                     max_fragments=50,
                     config='french'))

    def annee_du_mois_precedent(self):
        return self.date.year

    def mois_du_mois_precedent(self):
        return self.date.month

    def annee_du_mois_suivant(self):
        return self.date.year

    def mois_du_mois_suivant(self):
        return self.date.month


class Ephemeride:

    def __init__(self, d=None, url="", empty=True):
        if isinstance(d, date):
            self.date = d
            self.empty = empty
            self.url = url
        else:
            self.entree = d
            self.date = d.date
            self.empty = False
            self.url = self.entree.get_absolute_url()

        self._compute_pred_next_dates()
        self._build_agenda_for_ephemeride()

    def day(self):
        return self.date.day

    def month(self):
        return self.date.month

    def year(self):
        return self.date.year

    def _ephemeride(self, url):
        return "<div class=\"ephemeride\"><a href=\"" + url + "\"> \
            <div class=\"jour_semaine\">" + _(self.date.strftime("%A")) + "</div> \
            <div class=\"jour\">" + str(self.date.day) + "</div> \
            <div class=\"mois\">" + _(self.date.strftime("%B")) + "</div> \
            </a></div>"

    def _build_agenda_for_ephemeride(self):

        if self.date.day > 10:
            self.year_pred_month = self.date.year
            self.month_pred_month = self.date.month
            self.month_next_month = self.date.month + 1
            if self.month_next_month > 12:
                self.month_next_month = 1
                self.year_next_month = self.date.year + 1
            else:
                self.year_next_month = self.date.year
        else:
            self.year_next_month = self.date.year
            self.month_next_month = self.date.month
            self.month_pred_month = self.date.month - 1
            if self.month_pred_month == 0:
                self.month_pred_month = 12
                self.year_pred_month = self.date.year - 1
            else:
                self.year_pred_month = self.date.year
        entrees = EntreeAgenda.objects.filter((Q(date__year=self.year_pred_month) & Q(date__month=self.month_pred_month)) | (Q(date__year=self.year_next_month) & Q(date__month=self.month_next_month)))
        self.agenda = Agenda(entrees, 0, 'fr_FR.UTF-8')

    def ephemeride(self):
        if self.empty:
            return self._ephemeride(url="/fichier/agenda/add/?date=" + str(self.day()) + '/' + "{0:02d}".format(self.month()) + '/' + str(self.year()))
        else:
            return self._ephemeride(url=self.url)

    def _compute_pred_next_dates(self):
        prev_date = self.date - timedelta(days=1)
        self.prev_entree = EntreeAgenda.objects.filter(date=prev_date)
        if len(self.prev_entree) == 0:
            self.prev_entree = prev_date
        else:
            self.prev_entree = self.prev_entree[0]

        next_date = self.date + timedelta(days=1)
        self.next_entree = EntreeAgenda.objects.filter(date=next_date)
        if len(self.next_entree) == 0:
            self.next_entree = next_date
        else:
            self.next_entree = self.next_entree[0]

        un_an_avant_date = date(self.date.year - 1, self.date.month, self.date.day)
        self.un_an_avant_entree = EntreeAgenda.objects.filter(date=un_an_avant_date)
        if len(self.un_an_avant_entree) == 0:
            self.un_an_avant_entree = un_an_avant_date
        else:
            self.un_an_avant_entree = self.un_an_avant_entree[0]

        un_an_apres_date = date(self.date.year + 1, self.date.month, self.date.day)
        self.un_an_apres_entree = EntreeAgenda.objects.filter(date=un_an_apres_date)
        if len(self.un_an_apres_entree) == 0:
            self.un_an_apres_entree = un_an_apres_date
        else:
            self.un_an_apres_entree = self.un_an_apres_entree[0]


class Document(models.Model):

    titre = models.CharField(verbose_name="Nom", max_length=512)
    format_A4 = models.BooleanField(verbose_name="Présentation sous forme d'une unique page A4", default=False)
    contenu = RichTextField(verbose_name="Contenu", config_name='main_ckeditor', blank=True)

    date_creation = models.DateField(verbose_name="Date de création", default=timezone.now)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        self.date_derniere_modification = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('fichier:document', kwargs={'id': self.pk})

    def rechercher(search_text):

        if not search_text:
            return None

        search_vectors = SearchVector('contenu', weight='A', config='french') + \
            SearchVector('titre', weight='B', config='french')
        search_query = SearchQuery(search_text, config='french')

        return Document.objects.annotate(search=search_vectors).filter(search=search_query). \
            annotate(contenu_hl=SearchHeadline("contenu",
                                               search_query,
                                               start_sel="<span class=\"highlight\">",
                                               stop_sel="</span>",
                                               max_fragments=50,
                                               config='french'),
                     titre_hl=SearchHeadline("titre",
                                             search_query,
                                             start_sel="<span class=\"highlight\">",
                                             stop_sel="</span>",
                                             highlight_all=True,
                                             config='french'))
