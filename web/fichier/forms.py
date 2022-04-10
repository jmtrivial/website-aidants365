from django import forms
from .models import Fiche, EntreeGlossaire, EntreeAgenda, Categorie, Auteur, Theme, MotCle, CategorieLibre
from django.utils import timezone
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


class EntreeAgendaForm(WithUserForm):

    class Meta:
        model = EntreeAgenda

        fields = '__all__'


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
