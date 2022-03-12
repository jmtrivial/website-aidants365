from django import forms
from .models import Fiche
from django.utils import timezone


class FicheForm(forms.ModelForm):
    mots_cles_str = forms.CharField(label='Mots-clés', widget=forms.Textarea, required=False)
    utiliser_suivant = forms.BooleanField(label="Utiliser le prochain numéro disponible", initial=False, required=False)

    class Meta:
        model = Fiche

        localized_fields = ('date_creation', 'date_derniere_modification',)
        exclude = ('mots_cles', )

        widgets = {
            'reserves': forms.Textarea(),
            'lesplus': forms.Textarea(),
            'en_savoir_plus': forms.Textarea(),
        }
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            self.fields['mots_cles_str'].initial = ", ".join(x.nom for x in instance.mots_cles.all())
    