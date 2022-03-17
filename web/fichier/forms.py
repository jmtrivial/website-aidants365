from django import forms
from .models import Fiche
from django.utils import timezone


class FicheForm(forms.ModelForm):
    utiliser_suivant = forms.BooleanField(label="Utiliser le prochain numéro disponible", initial=False, required=False)

    class Meta:
        model = Fiche

        localized_fields = ('date_creation', 'date_derniere_modification',)

        fields = '__all__'
