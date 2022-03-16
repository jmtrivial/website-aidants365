from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models.signals import pre_save, post_init
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)


class Niveau(models.Model):

    class Applicabilite(models.TextChoices):
        A = 'A', "théorique"
        B = 'B', "intermédiaire"
        C = 'C', "pratique"

    ordre = models.IntegerField(verbose_name="Numéro", unique=True)
    code = models.CharField(verbose_name="Code", max_length=4, unique=True)
    nom = models.CharField(verbose_name="Nom", max_length=64)
    description = models.CharField(verbose_name="Description", max_length=256, blank=True, null=True)
    applicable = models.CharField(max_length=1, choices=Applicabilite.choices, default=Applicabilite.B)

    def couleur(self):
        if self.applicable == Niveau.Applicabilite.A:
            return "#fdfbe9"
        elif self.applicable == Niveau.Applicabilite.B:
            return "#d22439"
        else:
            return "#67b43f"

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


class MotCleManager(models.Manager):
    def create_or_new(self, mc):
        mc = mc.strip()
        qs = self.get_queryset().filter(nom__iexact=mc)
        if qs.exists():
            return qs.first(), False
        return MotCle.objects.create(nom=mc), True

    def comma_to_qs(self, motcles_str):
        final_ids = []
        if motcles_str != "":
            for mc in motcles_str.split(','):
                obj, created = self.create_or_new(mc)
                final_ids.append(obj.id)
        qs = self.get_queryset().filter(id__in=final_ids).distinct()
        return qs


class MotCle(models.Model):
    nom = models.CharField(verbose_name="Mot-clé", max_length=64)

    objects = MotCleManager()

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
    annee_publication = models.IntegerField(verbose_name="Année de publication", blank=True, null=True, default=2022)
    editeur = models.CharField(verbose_name="Éditeur", max_length=1024, blank=True)
    collection = models.CharField(verbose_name="Collection", max_length=1024, blank=True)
    format_bibl = models.CharField(verbose_name="Format", max_length=1024, blank=True)

    # uniquement si film
    realisateurs = models.CharField(verbose_name="Réalisateur(s)", max_length=1024, blank=True)
    annee_film = models.IntegerField(verbose_name="Année de production", blank=True, null=True, default=2022)
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
        return Fiche.objects.annotate(search=search_vectors).filter(search=SearchQuery(search_text, config='french'))


@receiver(pre_save, sender=Fiche)
def my_callback_pre_save(sender, instance, **kwargs):
    if instance.date_derniere_modification == instance.__original_date_derniere_modification:
        instance.date_derniere_modification = timezone.now()


@receiver(post_init, sender=Fiche)
def my_callback_post_save(sender, instance, *args, **kwargs):
    instance.__original_date_derniere_modification = instance.date_derniere_modification
