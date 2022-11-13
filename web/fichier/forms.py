from django import forms
from .models import Fiche, EntreeGlossaire, EntreeAgenda, Categorie, Auteur, Theme, Etiquette, Niveau, Document, EntetePage
from django.utils import timezone
from django.db import models
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib import admin
from django.urls import reverse
from sortedm2m.forms import SortedCheckboxSelectMultiple
from django.utils.encoding import force_str
from itertools import chain
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django_better_admin_arrayfield.forms.widgets import DynamicArrayWidget
import re

import logging
logger = logging.getLogger(__name__)


class MySortedCheckboxSelectMultiple(SortedCheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=(), renderer=None):

        # Normalize to strings
        if value:
            str_values = [force_str(v) for v in value]
        else:
            str_values = []

        selected = []
        unselected = []

        for option_value, option_label in chain(self.choices, choices):

            option_value = force_str(option_value)
            option_label = conditional_escape(force_str(option_label))
            item = {
                'option_label': option_label,
                'option_value': option_value
            }
            if option_value in str_values:
                selected.append(item)
            else:
                unselected.append(item)

        # replace template rendering by ad-hoc rendering to speedup the process
        html = '<div>'
        html += '<input type="hidden" id="' + attrs["id"] + '" name="' + name + '" value="">'
        html += '<select id="' + attrs["id"] + '_m2m" multiple>'
        html += ' ' + "".join(['<option value="' + row["option_value"] + '" selected>' + row["option_label"] + '</option>\n' for row in selected])
        html += ' ' + "".join(['<option value="' + row["option_value"] + '">' + row["option_label"] + '</option>\n' for row in unselected])
        html += '</select>'

        html += '</div>'

        return mark_safe(html)


class WithUserForm(forms.ModelForm):
    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.autofocus and self.autofocus in self.fields:
            self.fields[self.autofocus].widget.attrs.update({"autofocus": True})


class FicheForm(forms.ModelForm):
    utiliser_suivant = forms.BooleanField(label="Utiliser le prochain numéro disponible", initial=False, required=False)
    use_required_attribute = False

    class Meta:
        model = Fiche

        localized_fields = ('date_creation', 'date_derniere_modification',)

        exclude = ('urls', )

        widgets = {
            "themes": MySortedCheckboxSelectMultiple,
            "etiquettes": MySortedCheckboxSelectMultiple,
            "fiches_connexes": MySortedCheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if not instance:
            self.fields['utiliser_suivant'].initial = True
            self.fields['auteur'].initial = Auteur.get_connected_auteur(self.user)
        self.fields["themes"].widget.id_for_label = lambda x: "id_themes"
        self.fields["etiquettes"].widget.id_for_label = lambda x: "id_etiquettes"
        self.fields["fiches_connexes"].widget.id_for_label = lambda x: "id_fiches_connexes"

    def clean_numero(self):
        data = self.cleaned_data.get('numero', '')
        if not data:
            raise forms.ValidationError("Vous devez renseigner un numéro")
            # if you don't want this functionality, just remove it.
        if self.data.get('utiliser_suivant'):
            data = Fiche.get_numero_suivant(self.cleaned_data.get('auteur'))
        return data


class MyDynamicArrayWidget(DynamicArrayWidget):
    template_name = "fiches/dynamic_array.html"


class EntetePageForm(WithUserForm):
    autofocus = "texte"

    entete = True

    class Meta:
        model = EntetePage

        fields = '__all__'


class EntreeGlossaireForm(WithUserForm):

    autofocus = "entree"

    class Meta:
        model = EntreeGlossaire

        exclude = ('date_derniere_modification', 'urls', )

        widgets = {
            "formes_alternatives": MyDynamicArrayWidget
        }


class DocumentForm(WithUserForm):

    autofocus = "titre"

    class Meta:
        model = Document

        exclude = ('date_creation', 'date_derniere_modification', )


class EntreeAgendaForm(WithUserForm):

    autofocus = "themes"

    class Meta:
        model = EntreeAgenda

        exclude = ('date_derniere_modification', "urls")

        widgets = {
            "themes": MySortedCheckboxSelectMultiple,
            "etiquettes": MySortedCheckboxSelectMultiple,
            "fiches_associees": MySortedCheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["themes"].widget.id_for_label = lambda x: "id_themes"
        self.fields["etiquettes"].widget.id_for_label = lambda x: "id_etiquettes"
        self.fields["fiches_associees"].widget.id_for_label = lambda x: "id_fiches_associees"


class CategorieForm(WithUserForm):

    autofocus = "code"

    class Meta:
        model = Categorie

        fields = '__all__'


class ThemeForm(WithUserForm):

    autofocus = "nom"

    class Meta:
        model = Theme

        fields = '__all__'


class EtiquetteForm(WithUserForm):

    autofocus = "nom"

    class Meta:
        model = Etiquette

        fields = '__all__'


class NiveauForm(WithUserForm):

    autofocus = "nom"

    class Meta:
        model = Niveau

        fields = '__all__'


class TwoDifferentElementsForm(forms.Form):
    def clean(self):
        field1 = self.cleaned_data['element1']
        field2 = self.cleaned_data['element2']

        if field1 == field2:
            self.add_error("element2", "Les deux champs doivent être différents")

        return self.cleaned_data


class ThemeMergeForm(TwoDifferentElementsForm):
    element1 = forms.ModelChoiceField(queryset=Theme.objects.all().order_by("nom__unaccent"), required=True, label="Thème principal")
    element2 = forms.ModelChoiceField(queryset=Theme.objects.all().order_by("nom__unaccent"), required=True, label="Thème à intégrer dans le principal")


class EtiquetteMergeForm(TwoDifferentElementsForm):
    element1 = forms.ModelChoiceField(queryset=Etiquette.objects.all().order_by("nom__unaccent"), required=True, label="Étiquette principal")
    element2 = forms.ModelChoiceField(queryset=Etiquette.objects.all().order_by("nom__unaccent"), required=True, label="Étiquette à intégrer dans le principal")


class EntreeAgendaInvertForm(TwoDifferentElementsForm):
    element1 = forms.ModelChoiceField(queryset=EntreeAgenda.objects.all().order_by("date"), required=True, label="Entrée d'agenda")
    element2 = forms.ModelChoiceField(queryset=EntreeAgenda.objects.all().order_by("date"), required=True, label="Entrée d'agenda")


class EntreeAgendaInvertWithForm(forms.Form):
    element2 = forms.ModelChoiceField(queryset=EntreeAgenda.objects.all().order_by("date"), required=True, label="Entrée d'agenda")

    def __init__(self, *args, **kwargs):
        self.field1 = kwargs.pop('date1')
        super(EntreeAgendaInvertWithForm, self).__init__(*args, **kwargs)

    def clean(self):
        field2 = self.cleaned_data['element2']

        if self.field1 == field2:
            self.add_error("element2", "Les deux dates doivent être différentes")

        return self.cleaned_data
