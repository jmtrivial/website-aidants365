from django import forms
from .models import Fiche, EntreeGlossaire, EntreeAgenda, Categorie, Auteur, Theme, MotCle, CategorieLibre, Niveau, Document
from django.utils import timezone
from django.db import models
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib import admin
from django.urls import reverse

import logging
logger = logging.getLogger(__name__)


class WithUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class FicheForm(forms.ModelForm):
    utiliser_suivant = forms.BooleanField(label="Utiliser le prochain numéro disponible", initial=False, required=False)

    class Meta:
        model = Fiche

        localized_fields = ('date_creation', 'date_derniere_modification',)

        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if not instance:
            self.fields['utiliser_suivant'].initial = True
            self.fields['auteur'].initial = Auteur.get_connected_auteur(self.user)
        self.fields["categories_libres"].widget.id_for_label = lambda x: "id_categories_libres"
        self.fields["themes"].widget.id_for_label = lambda x: "id_themes"
        self.fields["mots_cles"].widget.id_for_label = lambda x: "id_mots_cles"
        self.fields["fiches_connexes"].widget.id_for_label = lambda x: "id_fiches_connexes"

    def clean_numero(self):
        data = self.cleaned_data.get('numero', '')
        if not data:
            raise forms.ValidationError("Vous devez renseigner un numéro")
            # if you don't want this functionality, just remove it.
        if self.data.get('utiliser_suivant'):
            data = Fiche.get_numero_suivant(self.cleaned_data.get('auteur'))
        return data


class EntreeGlossaireForm(WithUserForm):

    class Meta:
        model = EntreeGlossaire

        fields = '__all__'


class DocumentForm(WithUserForm):

    class Meta:
        model = Document

        exclude = ('date_creation', 'date_derniere_modification', )


class EntreeAgendaForm(WithUserForm):

    class Meta:
        model = EntreeAgenda

        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["themes"].widget.id_for_label = lambda x: "id_themes"
        self.fields["motscles"].widget.id_for_label = lambda x: "id_motscles"
        self.fields["fiches_associees"].widget.id_for_label = lambda x: "id_fiches_associees"


class CategorieForm(WithUserForm):

    class Meta:
        model = Categorie

        fields = '__all__'


class ThemeForm(WithUserForm):

    class Meta:
        model = Theme

        fields = '__all__'


class MotCleForm(WithUserForm):

    class Meta:
        model = MotCle

        fields = '__all__'


class CategorieLibreForm(WithUserForm):

    class Meta:
        model = CategorieLibre

        fields = '__all__'


class NiveauForm(WithUserForm):

    class Meta:
        model = Niveau

        fields = '__all__'


class MergeForm(forms.Form):
    def clean(self):
        field1 = self.cleaned_data['element1']
        field2 = self.cleaned_data['element2']

        if field1 == field2:
            self.add_error("element2", "Les deux champs doivent être différents")

        return self.cleaned_data


class ThemeMergeForm(MergeForm):
    element1 = forms.ModelChoiceField(queryset=Theme.objects.all().order_by("nom__unaccent"), required=True, label="Thème principal")
    element2 = forms.ModelChoiceField(queryset=Theme.objects.all().order_by("nom__unaccent"), required=True, label="Thème à intégrer dans le principal")


class MotCleMergeForm(MergeForm):
    element1 = forms.ModelChoiceField(queryset=MotCle.objects.all().order_by("nom__unaccent"), required=True, label="Mot-clé principal")
    element2 = forms.ModelChoiceField(queryset=MotCle.objects.all().order_by("nom__unaccent"), required=True, label="Mot-clé à intégrer dans le principal")


class CategorieLibreMergeForm(MergeForm):
    element1 = forms.ModelChoiceField(queryset=CategorieLibre.objects.all().order_by("nom__unaccent"), required=True, label="Catégorie libre principal")
    element2 = forms.ModelChoiceField(queryset=CategorieLibre.objects.all().order_by("nom__unaccent"), required=True, label="Catégorie libre à intégrer dans le principal")
