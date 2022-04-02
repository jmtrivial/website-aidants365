from django.contrib import admin
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect

from .models import Niveau, Categorie, Fiche, Auteur, Theme, MotCle, CategorieLibre, TypeCategorie, EntreeGlossaire, EntreeAgenda
from .forms import FicheForm
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

admin.site.register(Niveau)
admin.site.register(TypeCategorie)
admin.site.register(Categorie)
admin.site.register(Auteur)


class CategorieLibreAdmin(admin.ModelAdmin):
    search_fields = ('nom', )


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

    autocomplete_fields = ['categories_libres', 'themes', 'fiches_connexes', 'mots_cles']

    fields = (("niveau", "categorie1"),
              ("categorie2", "categorie3", "categories_libres"),
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

    def get_form(self, request, obj=None, **kwargs):
        form = super(FicheAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['auteur'].initial = Auteur.get_connected_auteur(request.user)
        return form

    def render_change_form(self, request, context, *args, **kwargs):
        """We need to update the context to show the button."""
        context.update({'show_save_and_view': True})
        return super().render_change_form(request, context, *args, **kwargs)

    def response_post_save_change(self, request, obj):
        """This method is called by `self.changeform_view()` when the form
        was submitted successfully and should return an HttpResponse.
        """
        # Check that you clicked the button `_save_and_view`
        if '_save_and_view' in request.POST:
            view_url = obj.get_absolute_url()

            # And redirect
            return HttpResponseRedirect(view_url)
        else:
            # Otherwise, use default behavior
            return super().response_post_save_change(request, obj)


admin.site.register(MotCle, MotCleAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(CategorieLibre, CategorieLibreAdmin)
admin.site.register(Fiche, FicheAdmin)


class EntreeGlossaireAdmin(admin.ModelAdmin, DynamicArrayMixin):
    search_fields = ('entree', )

    @admin.display(empty_value='???', description='Lien')
    def custom_link(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">voir l\'entrée</a>')

    def render_change_form(self, request, context, *args, **kwargs):
        """We need to update the context to show the button."""
        context.update({'show_save_and_view': True})
        return super().render_change_form(request, context, *args, **kwargs)

    def response_post_save_change(self, request, obj):
        """This method is called by `self.changeform_view()` when the form
        was submitted successfully and should return an HttpResponse.
        """
        # Check that you clicked the button `_save_and_view`
        if '_save_and_view' in request.POST:
            view_url = obj.get_absolute_url()

            # And redirect
            return HttpResponseRedirect(view_url)
        else:
            # Otherwise, use default behavior
            return super().response_post_save_change(request, obj)


admin.site.register(EntreeGlossaire, EntreeGlossaireAdmin)


class EntreeAgendaAdmin(admin.ModelAdmin):
    search_fields = ('notes', )

    @admin.display(empty_value='???', description='Lien')
    def custom_link(self, obj):
        return mark_safe(f'<a href="{obj.get_absolute_url()}">voir l\'entrée</a>')

    autocomplete_fields = ['themes', 'motscles', 'fiches_associees']

    def render_change_form(self, request, context, *args, **kwargs):
        """We need to update the context to show the button."""
        context.update({'show_save_and_view': True})
        return super().render_change_form(request, context, *args, **kwargs)

    def response_post_save_change(self, request, obj):
        """This method is called by `self.changeform_view()` when the form
        was submitted successfully and should return an HttpResponse.
        """
        # Check that you clicked the button `_save_and_view`
        if '_save_and_view' in request.POST:
            view_url = obj.get_absolute_url()

            # And redirect
            return HttpResponseRedirect(view_url)
        else:
            # Otherwise, use default behavior
            return super().response_post_save_change(request, obj)


admin.site.register(EntreeAgenda, EntreeAgendaAdmin)
