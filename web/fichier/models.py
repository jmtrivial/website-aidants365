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
from .utils import Ephemeride, table, arrayToString
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchHeadline
from sortedm2m.fields import SortedManyToManyField
from .utils import message_glossaire, message_sortable

import logging
logger = logging.getLogger(__name__)


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


class Niveau(models.Model):

    class Applicabilite(models.TextChoices):
        A = 'A', "informatif"
        B = 'B', "pratique"
        C = 'C', "opérationnel"

    couleur_A = "#fdfbe9"
    couleur_B = "#ea841d"
    couleur_C = "#67b43f"

    ordre = models.IntegerField(verbose_name="Numéro", unique=True)
    code = models.CharField(verbose_name="Code", max_length=4, unique=True)
    nom = models.CharField(verbose_name="Nom", max_length=64)
    description = models.CharField(verbose_name="Description", max_length=256, blank=True, null=True)
    applicable = models.CharField(max_length=1, choices=Applicabilite.choices, default=Applicabilite.B)

    def couleur(self):
        if self.applicable == Niveau.Applicabilite.A:
            return Niveau.couleur_A
        elif self.applicable == Niveau.Applicabilite.B:
            return Niveau.couleur_B
        else:
            return Niveau.couleur_C

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"

    def __str__(self):
        return " ".join(["{:02d}".format(self.ordre), self.code])

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, Niveau)


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

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.code

    def description_longue(self):
        return self.code + " — " + self.nom

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, Categorie)

    def associated_entries(self):
        result = []

        # Liste des entrées d'agenda associées à cette catégorie
        result += Fiche.objects.filter(Q(categorie1=self.id) | Q(categorie2=self.id) | Q(categorie3=self.id))

        return result


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


class CategorieLibre(models.Model):
    nom = models.CharField(verbose_name="Nom de la catégorie libre", max_length=64, unique=True, blank=False)

    class Meta:
        verbose_name = "Catégorie libre"
        verbose_name_plural = "Catégories libres"

    def __str__(self):
        return self.nom

    def description_longue(self):
        return self.nom

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, CategorieLibre)

    def associated_entries(self):
        result = []

        # Liste des entrées d'agenda associées à cette catégorie
        result += Fiche.objects.filter(categories_libres=self.id)

        return result


class MotCle(models.Model):
    nom = models.CharField(verbose_name="Mot-clé", max_length=64, unique=True, blank=False)

    class Meta:
        verbose_name = "Mot-clé"
        verbose_name_plural = "Mot-clés"

    def __str__(self):
        return self.nom

    def description_longue(self):
        return self.nom

    def rechercher(search_text):
        return rechercher_nom_simple(search_text, MotCle)

    def associated_entries(self):
        result = []
        # Liste des fiches ayant ce mot-clé
        result += Fiche.objects.filter(mots_cles=self.id)

        # Liste des entrées d'agenda ayant ce mot-clé
        result += EntreeAgenda.objects.filter(motscles=self.id)

        return result


class Theme(models.Model):
    nom = models.CharField(verbose_name="Thème", max_length=64, unique=True, blank=False)

    class Meta:
        verbose_name = "Thème"
        verbose_name_plural = "Thèmes"

    def __str__(self):
        return self.nom

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


class Fiche(models.Model):
    # entête

    niveau = models.ForeignKey(Niveau, verbose_name="Niveau", on_delete=models.RESTRICT)
    categorie1 = models.ForeignKey(Categorie, verbose_name="Catégorie principale", on_delete=models.RESTRICT, related_name='%(class)s_categorie1')
    categorie2 = models.ForeignKey(Categorie, verbose_name="Deuxième catégorie", on_delete=models.SET_NULL, related_name='%(class)s_categorie2', blank=True, null=True)
    categorie3 = models.ForeignKey(Categorie, verbose_name="Troisième catégorie", on_delete=models.SET_NULL, related_name='%(class)s_categorie3', blank=True, null=True)
    categories_libres = SortedManyToManyField(CategorieLibre, verbose_name="Catégories libres", blank=True, help_text=message_sortable)

    auteur = models.ForeignKey(Auteur, verbose_name="Auteur", on_delete=models.RESTRICT)
    marque = models.BooleanField(verbose_name="Entrée de qualité", default=False)

    numero = models.IntegerField(verbose_name="Numéro", default=9999)
    titre_fiche = models.CharField(verbose_name="Titre de la fiche", max_length=256)
    sous_titre = models.CharField(verbose_name="Sous-titre", max_length=256, blank=True)

    date_creation = models.DateField(verbose_name="Date de création", default=timezone.now)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

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
    mots_cles = SortedManyToManyField(MotCle, verbose_name="Mots-clés", blank=True, help_text=message_sortable)

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
            annotate(agg_contenu=Concat("sous_titre", Value(" "), "presentation", Value(" "), "problematique", Value(" "), "quatrieme_de_couverture", Value(" "),
                                        "plan_du_site", Value(" Focus "), "detail_focus", Value(" "), "focus", Value(" "), "titre", Value(" "), "editeur", Value(" "), "auteurs", Value(" "), "collection",
                                        "partenaires", Value(" "), "reserves", Value(" "), "lesplus", Value(" "), "en_savoir_plus", output_field=models.CharField())). \
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


class EntreeGlossaire(models.Model):

    class Meta:
        verbose_name = "Entrée du glossaire"
        verbose_name_plural = "Entrées du glossaire"

    def __str__(self):
        return self.entree

    entree = models.CharField(verbose_name="Entrée", max_length=128, unique=False, blank=False)
    formes_alternatives = ArrayField(models.CharField(max_length=128, blank=True), verbose_name="Formes alternatives (pluriels, abréviations, etc)", blank=True, null=True)

    definition = RichTextField(verbose_name="Définition", config_name='main_ckeditor', blank=True)

    def get_absolute_url(self):
        return reverse('fichier:entree_glossaire', kwargs={'id': self.pk})

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

    date = models.DateField()

    marque = models.BooleanField(verbose_name="Entrée de qualité", default=False)

    themes = SortedManyToManyField(Theme, verbose_name="Thèmes associés", blank=True, help_text=message_sortable)
    motscles = SortedManyToManyField(MotCle, verbose_name="Mots-clés associés", blank=True, help_text=message_sortable)

    notes = RichTextField(verbose_name="Notes", config_name='main_ckeditor', blank=True, help_text=message_glossaire)

    fiches_associees = SortedManyToManyField(Fiche, verbose_name="Fiches associées", blank=True, help_text=message_sortable)

    def get_absolute_url(self):
        return reverse('fichier:entree_agenda', kwargs={'year': self.date.year, 'month': self.date.month, 'day': self.date.day})

    def __str__(self):
        texte = self.date.strftime("%d/%m/%Y")
        if self.marque:
            return texte + " ☑"
        else:
            return texte

    def ephemeride(self):
        e = Ephemeride(self.date, self.get_absolute_url(), False)
        return e.ephemeride()

    def rechercher(search_text):
        from django.contrib.postgres.search import SearchVector
        from django.contrib.postgres.search import SearchQuery

        if not search_text:
            return None

        search_vectors = SearchVector('notes', weight='A', config='french')
        search_query = SearchQuery(search_text, config='french')
        return EntreeAgenda.objects.annotate(search=search_vectors).filter(search=search_query). \
            annotate(notes_hl=SearchHeadline("notes",
                     search_query,
                     start_sel="<span class=\"highlight\">",
                     stop_sel="</span>",
                     max_fragments=50,
                     config='french'))


class Document(models.Model):

    titre = models.CharField(verbose_name="Nom", max_length=512)
    format_A4 = models.BooleanField(verbose_name="Présentation sous forme d'une unique page A4", default=False)
    contenu = RichTextField(verbose_name="Contenu", config_name='main_ckeditor', blank=True)

    date_creation = models.DateField(verbose_name="Date de création", default=timezone.now)
    date_derniere_modification = models.DateTimeField(verbose_name="Dernière modification", auto_now=True)

    def __str__(self):
        return self.titre

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


@receiver(pre_save, sender=Fiche)
def my_callback_pre_save(sender, instance, **kwargs):
    if instance.date_derniere_modification == instance.__original_date_derniere_modification:
        instance.date_derniere_modification = timezone.now()


@receiver(post_init, sender=Fiche)
def my_callback_post_save(sender, instance, *args, **kwargs):
    instance.__original_date_derniere_modification = instance.date_derniere_modification
