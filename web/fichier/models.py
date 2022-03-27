from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models.signals import pre_save, post_init
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User
from django_better_admin_arrayfield.models.fields import ArrayField
import re
import html.entities
from django.utils.html import strip_tags
from django.utils.text import Truncator

import logging
logger = logging.getLogger(__name__)

table = {k: '&{};'.format(v) for k, v in html.entities.codepoint2name.items()}


class Niveau(models.Model):

    class Applicabilite(models.TextChoices):
        A = 'A', "théorique"
        B = 'B', "intermédiaire"
        C = 'C', "pratique"

    couleur_A = "#fdfbe9"
    couleur_B = "#d22439"
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
    nom = models.CharField(verbose_name="Nom de la catégorie libre", max_length=64)

    class Meta:
        verbose_name = "Catégorie libre"
        verbose_name_plural = "Catégories libres"

    def __str__(self):
        return self.nom

    def description_longue(self):
        return self.nom


class MotCle(models.Model):
    nom = models.CharField(verbose_name="Mot-clé", max_length=64)

    class Meta:
        verbose_name = "Mot-clé"
        verbose_name_plural = "Mot-clés"

    def __str__(self):
        return self.nom

    def description_longue(self):
        return self.nom


class Theme(models.Model):
    nom = models.CharField(verbose_name="Thème", max_length=64)

    class Meta:
        verbose_name = "Thème"
        verbose_name_plural = "Thèmes"

    def __str__(self):
        return self.nom

    def description_longue(self):
        return self.nom


class Fiche(models.Model):
    # entête

    niveau = models.ForeignKey(Niveau, verbose_name="Niveau", on_delete=models.RESTRICT)
    categorie1 = models.ForeignKey(Categorie, verbose_name="Catégorie principale", on_delete=models.RESTRICT, related_name='%(class)s_categorie1')
    categorie2 = models.ForeignKey(Categorie, verbose_name="Catégorie secondaire", on_delete=models.SET_NULL, related_name='%(class)s_categorie2', blank=True, null=True)
    categorie3 = models.ForeignKey(Categorie, verbose_name="Catégorie 3", on_delete=models.SET_NULL, related_name='%(class)s_categorie3', blank=True, null=True)
    categories_libres = models.ManyToManyField(CategorieLibre, verbose_name="Catégories libres", blank=True)

    auteur = models.ForeignKey(Auteur, verbose_name="Auteur", on_delete=models.RESTRICT)
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
    format_bibl = models.CharField(verbose_name="Format", max_length=1024, blank=True)

    # uniquement si film
    realisateurs = models.CharField(verbose_name="Réalisateur(s)", max_length=1024, blank=True)
    annee_film = models.IntegerField(verbose_name="Année de production", blank=True, null=True)
    diffusion = models.CharField(verbose_name="Diffusion", max_length=1024, blank=True, null=True)
    duree = models.CharField(verbose_name="Durée", max_length=32, blank=True)
    production = models.CharField(verbose_name="Production", max_length=1024, blank=True)

    # uniquement si site
    partenaires = models.CharField(verbose_name="Partenaires", max_length=1024, blank=True, null=True)

    themes = models.ManyToManyField(Theme, verbose_name="Thèmes", blank=True)
    mots_cles = models.ManyToManyField(MotCle, verbose_name="Mots-clés", blank=True)

    # corps
    presentation = RichTextField(verbose_name="Présentation", config_name='main_ckeditor', blank=True)

    problematique = RichTextField(verbose_name="Problématique", config_name='main_ckeditor', blank=True)

    # uniquement si biblio
    quatrieme_de_couverture = RichTextField(verbose_name="Quatrième de couverture", config_name='main_ckeditor', blank=True)

    # uniquement si site
    plan_du_site = RichTextField(verbose_name="Plan du site", config_name='main_ckeditor', blank=True)

    detail_focus = models.CharField(verbose_name="Détail du focus (placé après le mot \"Focus\")", max_length=1024, blank=True)

    focus = RichTextField(verbose_name="Focus", config_name='main_ckeditor', blank=True)

    # pied de page
    reserves = RichTextField(verbose_name="Réserves", config_name='main_ckeditor', blank=True)
    lesplus = RichTextField(verbose_name="Les plus", config_name='main_ckeditor', blank=True)
    en_savoir_plus = RichTextField(verbose_name="En savoir plus", config_name='main_ckeditor', blank=True)
    fiches_connexes = models.ManyToManyField("self", verbose_name="Fiches connexes", blank=True)

    class Meta:
        verbose_name = "Fiche"
        verbose_name_plural = "Fiches"
        ordering = ["auteur", "numero"]

    def get_descriptions(self):
        return [self.presentation, self.problematique, self.quatrieme_de_couverture,
                self.plan_du_site, self.focus,
                self.reserves, self.lesplus, self.en_savoir_plus]

    def __str__(self):
        return " ".join(map(str, [self.niveau, self.categorie1, self.auteur, "{:04d}".format(self.numero), self.titre_fiche]))

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

        search_vectors = SearchVector('presentation', weight='A', config='french') + \
            SearchVector('problematique', weight='A', config='french') + \
            SearchVector('quatrieme_de_couverture', weight='A', config='french') + \
            SearchVector('plan_du_site', weight='A', config='french') + \
            SearchVector('focus', weight='A', config='french') + \
            SearchVector('auteur__code', weight='D', config='french') + \
            SearchVector('auteur__nom', weight='D', config='french') + \
            SearchVector('niveau__nom', weight='B', config='french') + \
            SearchVector('categorie1__nom', weight='B', config='french') + \
            SearchVector('categorie2__nom', weight='B', config='french') + \
            SearchVector('categorie3__nom', weight='B', config='french') + \
            SearchVector('niveau__code', weight='B', config='french') + \
            SearchVector('categorie1__code', weight='B', config='french') + \
            SearchVector('categorie2__code', weight='B', config='french') + \
            SearchVector('categorie3__code', weight='B', config='french') + \
            SearchVector('categories_libres', weight='C', config='french') + \
            SearchVector('titre_fiche', weight='A', config='french') + \
            SearchVector('sous_titre', weight='A', config='french') + \
            SearchVector('titre', weight='D', config='french') + \
            SearchVector('editeur', weight='D', config='french') + \
            SearchVector('auteurs', weight='D', config='french') + \
            SearchVector('collection', weight='D', config='french') + \
            SearchVector('partenaires', weight='D', config='french') + \
            SearchVector('reserves', weight='C', config='french') + \
            SearchVector('lesplus', weight='C', config='french') + \
            SearchVector('en_savoir_plus', weight='C', config='french')
        return Fiche.objects.annotate(search=search_vectors).filter(search=SearchQuery(search_text.translate(table), config='french'))


class EntreeGlossaire(models.Model):

    class Meta:
        verbose_name = "Entrée du glossaire"
        verbose_name_plural = "Entrées du glossaire"

    def __str__(self):
        return self.entree

    entree = models.CharField(verbose_name="Entrée", max_length=128)
    formes_alternatives = ArrayField(models.CharField(max_length=128, blank=True), verbose_name="Formes alternatives (pluriels, abréviations, etc)", blank=True, null=True)

    definition = RichTextField(verbose_name="Définition", config_name='main_ckeditor', blank=True)

    def get_absolute_url(self):
        return reverse('fichier:entree_glossaire', kwargs={'id': self.pk})

    def ajouter_liens_entree(self, text, entree):
        return re.sub(r'\[(%s)\]' % entree.translate(table), r'<a title="%s" class="glossaire" href="/fichier/glossaire/%s/">\1</a>' % (Truncator(strip_tags(self.definition)).words(64), str(self.id)), text)

    def ajouter_liens(self, text):
        result = self.ajouter_liens_entree(text, self.entree)

        if self.formes_alternatives:
            for fa in self.formes_alternatives:
                result = self.ajouter_liens_entree(result, fa)

        return result

    def matching_fiches(self):
        result = []
        e_html = self.entree.translate(table)
        if self.formes_alternatives:
            fa_html = [fa.translate(table) for fa in self.formes_alternatives]
        else:
            fa_html = []

        for f in Fiche.objects.filter():
            for t in f.get_descriptions():
                if re.search(r'\[%s\]' % e_html, str(t)):
                    result.append(f)
                    break
                else:
                    found = False
                    for fa in fa_html:
                        if re.search(r'\[%s\]' % fa, str(t)):
                            result.append(f)
                            found = True
                            break
                    if found:
                        break

        return result


@receiver(pre_save, sender=Fiche)
def my_callback_pre_save(sender, instance, **kwargs):
    if instance.date_derniere_modification == instance.__original_date_derniere_modification:
        instance.date_derniere_modification = timezone.now()


@receiver(post_init, sender=Fiche)
def my_callback_post_save(sender, instance, *args, **kwargs):
    instance.__original_date_derniere_modification = instance.date_derniere_modification
