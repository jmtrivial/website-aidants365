from django.contrib import admin
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect

from .models import Niveau, Categorie, Fiche, Auteur, Theme, MotCle, TypeCategorie, EntreeGlossaire, EntreeAgenda
from .forms import FicheForm
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

admin.site.register(Niveau)
admin.site.register(TypeCategorie)
admin.site.register(Categorie)
admin.site.register(Auteur)



class ThemeAdmin(admin.ModelAdmin):
    search_fields = ('nom', )


class MotCleAdmin(admin.ModelAdmin):
    search_fields = ('nom', )


class FicheAdmin(admin.ModelAdmin):
    form = FicheForm

    save_on_top = True
    search_fields = ("niveau__nom", "categorie1__nom", "auteur__nom", "niveau__code", "categorie1__code", "auteur__code", "numero", "titre_fiche", )

    list_display = ("__str__", "niveau", "categorie1", "auteur", "numero", "titre_fiche", "date_derniere_modification", "custom_link")

    @admin.display(empty_value='???', description='Lien')
    def custom_link(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">voir la fiche</a>')

    fields = (("niveau", "categorie1"),
              ("categorie2", "categorie3"),
              ("auteur", "numero", "utiliser_suivant", "date_creation"),
              "titre_fiche",
              "sous_titre",
              "url",
              "titre",
              "auteurs",
              "annee_publication",
              "editeur",
              "collection",
              "format_bibl",
              "realisateurs",
              "annee_film",
              "diffusion",
              "duree",
              "production",
              "partenaires",
              "themes",
              "mots_cles",
              "presentation",
              "problematique",
              "quatrieme_de_couverture",
              "plan_du_site",
              "detail_focus",
              "focus",
              "reserves",
              "lesplus",
              "en_savoir_plus",
              "fiches_connexes", )


admin.site.register(MotCle, MotCleAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Fiche, FicheAdmin)


class EntreeGlossaireAdmin(admin.ModelAdmin, DynamicArrayMixin):
    search_fields = ('entree', )

    @admin.display(empty_value='???', description='Lien')
    def custom_link(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">voir l\'entrée</a>')


admin.site.register(EntreeGlossaire, EntreeGlossaireAdmin)


class EntreeAgendaAdmin(admin.ModelAdmin):
    search_fields = ('notes', )

    @admin.display(empty_value='???', description='Lien')
    def custom_link(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">voir l\'entrée</a>')


admin.site.register(EntreeAgenda, EntreeAgendaAdmin)
