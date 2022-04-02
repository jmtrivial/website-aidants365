from django import forms
from .models import Fiche, EntreeGlossaire, EntreeAgenda, Theme
from django.utils import timezone
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib import admin
from django.urls import reverse

import logging
logger = logging.getLogger(__name__)


class FicheForm(forms.ModelForm):
    utiliser_suivant = forms.BooleanField(label="Utiliser le prochain numéro disponible", initial=False, required=False)

    class Meta:
        model = Fiche

        localized_fields = ('date_creation', 'date_derniere_modification',)

        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if not instance:
            self.fields['utiliser_suivant'].initial = True


class EntreeGlossaireForm(forms.ModelForm):

    class Meta:
        model = EntreeGlossaire

        fields = '__all__'


class EntreeAgendaForm(forms.ModelForm):

    class Meta:
        model = EntreeAgenda

        fields = '__all__'
