from django.contrib import admin
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect

from .models import Niveau, Categorie, Fiche, Auteur, Theme, MotCle, CategorieLibre, TypeCategorie
from .forms import FicheForm

admin.site.register(Niveau)
admin.site.register(TypeCategorie)
admin.site.register(CategorieLibre)
admin.site.register(Categorie)
admin.site.register(Auteur)
admin.site.register(Theme)
admin.site.register(MotCle)


class FicheAdmin(admin.ModelAdmin):
    form = FicheForm

    save_on_top = True
    search_fields = ['titre_fiche']


    fields = (("niveau", "categorie1"),
              ("categorie2", "categorie3", "categories_libres"),
              ("auteur", "numero", "utiliser_suivant"),
              "titre_fiche",
              "sous_titre",
              ("date_creation", "date_derniere_modification"),
              "url",
              "titre",
              "auteurs",
              "date_publication",
              "editeur",
              "format_bibl",
              "partenaires",
              "themes",
              "mots_cles_str",
              "presentation",
              "plan_du_site",
              "focus",
              "reserves",
              "lesplus",
              "en_savoir_plus",
              "fiches_connexes", )

    def mots_cles_list(self, obj):
        mots_cles_list = ", ".join([f"<a href='/fiches/?mots_cles__nom={x.nom}'>{x.nom}</a>" for x in obj.mots_cles.all()])
        return mark_safe(mots_cles_list)

    def save_model(self, request, obj, form, change):
        mots_cles_str = form.cleaned_data.get('mots_cles_str')
        mots_cles_qs = MotCle.objects.comma_to_qs(mots_cles_str)
        utiliser_suivant = form.cleaned_data.get('utiliser_suivant')

        if not obj.id:
            obj.save()

        if utiliser_suivant:
            obj.numero = Fiche.get_numero_suivant(form.cleaned_data.get('auteur'))

        obj.mots_cles.clear()
        obj.mots_cles.add(*mots_cles_qs)

        obj.save()
    
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
        


admin.site.register(Fiche, FicheAdmin)
