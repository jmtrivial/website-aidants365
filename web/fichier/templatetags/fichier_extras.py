from django import template
from django.utils.safestring import mark_safe
from fichier.models import Categorie, Niveau, EntreeGlossaire, EntreeAgenda
import re
from fichier.utils import Agenda
from django.urls import reverse
from datetime import datetime
from sortedm2m.fields import SortedMultipleChoiceField
from ckeditor.fields import RichTextFormField
from string import ascii_uppercase

import html.entities

table = {k: '&{};'.format(v) for k, v in html.entities.codepoint2name.items()}


register = template.Library()


@register.filter
def enlever_tiret_bas(value):
    return value.replace("_", "")


@register.filter
def nomenclature(value):
    return str(value)


@register.filter
def carre_colore(value):
    return mark_safe("<div class=\"carre\" style=\"background-color: " + value + "\"> </div>")


@register.filter
def number_xxxx(value):
    return "{:04d}".format(value)


@register.filter
def nom_mois(value):
    return Agenda.month_name[value].lower()


@register.simple_tag
def show_year(agenda, year):
    return mark_safe(agenda.year(year))


@register.simple_tag
def show_month(agenda, year, month):
    return mark_safe(agenda.month(year, month))


def get_url_jour_missing(date):
    return reverse("fichier:object_add", kwargs={"classname": "agenda"}) + "?date=" + str(date.day) + "/" + str(date.month) + "/" + str(date.year)


def get_url_jour(date):
    return reverse("fichier:entree_agenda", kwargs={"year": date.year, "month": date.month, "day": date.day})


def get_day_name(date):
    return str(date.day) + " " + Agenda.month_name[date.month].lower() + " " + str(date.year)


def lien_jour(url, text, class_name):
    return mark_safe('<a class="' + class_name + '" href="' + url + '">' + text + "</a>")


def lien_jour_prepostfix(day, prefix, postfix, name):
    if isinstance(day, EntreeAgenda):
        url = get_url_jour(day.date)
        text = get_day_name(day.date)
        classname = ""
    else:
        url = get_url_jour_missing(day)
        text = get_day_name(day)
        classname = " missing-day"
    return lien_jour(url, prefix + " " + text + " " + postfix, "lien_" + name + classname)


@register.simple_tag
def lien_jour_precedent(day):
    return lien_jour_prepostfix(day, "◂", " ", "pred")


@register.simple_tag
def lien_jour_un_an_avant(day):
    return lien_jour_prepostfix(day, "◂◂", "", "pred")


@register.simple_tag
def lien_jour_suivant(day):
    return lien_jour_prepostfix(day, "", "▸", "next")


@register.simple_tag
def lien_jour_un_an_apres(day):
    return lien_jour_prepostfix(day, "", "▸▸", "next")


@register.simple_tag
def lien_mois_precedent(year, month):
    month -= 1
    if month == 0:
        year -= 1
        month = 12
    return mark_safe('<a class="lien_pred" href="' + reverse("fichier:agenda_month", kwargs={"year": year, "month": month}) + '">◂ ' + Agenda.month_name[month] + " " + str(year) + "</a>")


@register.simple_tag
def lien_mois_suivant(year, month):
    month += 1
    if month == 13:
        year += 1
        month = 1
    return mark_safe('<a class="lien_next" href="' + reverse("fichier:agenda_month", kwargs={"year": year, "month": month}) + '">' + Agenda.month_name[month] + " " + str(year) + " ▸</a>")


@register.simple_tag
def lien_annee_suivante(year):
    year += 1
    return mark_safe('<a class="lien_next" href="' + reverse("fichier:agenda_year", kwargs={"year": year}) + '">' + str(year) + " ▸</a>")


@register.simple_tag
def lien_annee_precedente(year):
    year -= 1
    return mark_safe('<a class="lien_pred" href="' + reverse("fichier:agenda_year", kwargs={"year": year}) + '">◂ ' + str(year) + "</a>")


@register.filter
def affiche_si_existe(value, arg):
    if value:
        if type(value) == str and value.startswith("<p>"):
            return "<p><strong>" + arg + "&nbsp;:</strong> " + value[3:]
        else:
            return "<strong>" + arg + "&nbsp;:</strong> " + str(value)
    else:
        return ""


@register.simple_tag
def affiche_bloc_si_existe(value, name1, name2):
    if value:
        if name2:
            return "<p><strong>" + name1 + " " + name2 + "&nbsp;:</strong> " + value + "</p>"
        else:
            return "<p><strong>" + name1 + "&nbsp;:</strong> " + value + "</p>"
    else:
        return ""


@register.filter
def inside_si_existe(value, arg):
    if value:
        return "<" + arg + ">" + value + "</" + arg + ">"
    else:
        return ""


@register.filter
def cliquable(value):
    if value:
        return "<a href=\"" + value + "\">" + value + "</a>"
    else:
        return ""


@register.filter
def virgule_ou_vide(value):
    if value:
        return ", " + value
    else:
        return ""


@register.simple_tag
def set_listes_categories_modifieurs_champs():
    result = "<script type=\"text/javascript\">\n"
    result += "document.categories_bibio = ["
    result += ", ".join(["\"" + str(x[0]) + "\"" for x in Categorie.objects.filter(is_biblio=True).values_list('id')])
    result += "];\n"
    result += "document.categories_site = ["
    result += ", ".join(["\"" + str(x[0]) + "\"" for x in Categorie.objects.filter(is_site=True).values_list('id')])
    result += "];\n"
    result += "document.categories_film = ["
    result += ", ".join(["\"" + str(x[0]) + "\"" for x in Categorie.objects.filter(is_film=True).values_list('id')])
    result += "];\n"
    result += "</script>\n"
    return mark_safe(result)


@register.simple_tag
def get_carre_colore_A():
    return carre_colore(Niveau.couleur_A)


@register.simple_tag
def get_carre_colore_B():
    return carre_colore(Niveau.couleur_B)


@register.simple_tag
def get_carre_colore_C():
    return carre_colore(Niveau.couleur_C)


@register.simple_tag
def get_nom_niveau_A():
    return Niveau.Applicabilite.A.label


@register.simple_tag
def get_nom_niveau_B():
    return Niveau.Applicabilite.B.label


@register.simple_tag
def get_nom_niveau_C():
    return Niveau.Applicabilite.C.label


@register.simple_tag
def lien_interne(texte, ok, url):
    if ok:
        return '<a class="interne" href="' + url + '>' + texte + "</a>"
    else:
        return texte


@register.simple_tag
def liste_niveaux(niveau_code):
    match = {"A": Niveau.Applicabilite.A, "B": Niveau.Applicabilite.B, "C": Niveau.Applicabilite.C}
    niv = Niveau.objects.filter(applicable=match[niveau_code])
    result = ""
    for n in niv:
        if result != "":
            result += ", "
        result += '<a href="' + reverse("fichier:index_niveau", kwargs={"id": n.id}) + '">' + str(n) + "</a>"
    result += ""
    return mark_safe(result)


@register.filter
def ajouter_glossaire(texte, liens):
    result = texte

    if liens:
        result = re.sub(r'\[([^\]<>]*)\]', lambda x: x.group() if x.group() == "[...]" else '<a class="glossaire" title="' + x.group()[1:-1] + '" href="/fichier/glossaire/search/' + x.group()[1:-1] + '/">' + x.group()[1:-1] + '</a>', result)
    else:
        result = re.sub(r'\[([^\]<>]*)\]', r'<span class="glossaire">\1</a>', result)

    return result


@register.filter
def ajouter_liens(texte):
    # on ajoute les liens des urls si elles existent
    pat1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
    return pat1.sub(r'\1<a href="\2">\2</a>', texte)


@register.filter
def extract_id_from_m2m(texte):
    return texte.split("\"")[1].split("_")[-1]


@register.filter
def extract_id_from_cb_m2m(texte):
    return texte.split("\"")[-8]  # pas super robuste, mais si on ne change pas les dépendances, ça va marcher... ingénierie inverse


def extract_field_id(texte):
    return "_".join(texte.split("\"")[1].split("_")[:-1])


def extract_field_id_small(texte):
    return "_".join(texte.split("\"")[1].split("_")[1:-1])


@register.simple_tag
def get_field_id_m2m(selected, unselected):
    if selected:
        return extract_field_id(selected[0]["label_for"])
    elif unselected:
        return extract_field_id(unselected[0]["label_for"])
    else:
        return "unset"


@register.simple_tag
def get_field_id_small_m2m(selected, unselected):
    if selected:
        return extract_field_id_small(selected[0]["label_for"])
    elif unselected:
        return extract_field_id_small(unselected[0]["label_for"])
    else:
        return "unset"


@register.filter
def label_with_stars(field):
    if (isinstance(field.field, SortedMultipleChoiceField)):
        return field.label_tag().replace(":", "<sup>*</sup>")
    if (isinstance(field.field, RichTextFormField)):
        return field.label_tag().replace(":", "<sup>**</sup>")
    else:
        return field.label_tag().replace(":", "")


def button_new(txt, link, title):
    return mark_safe('<div class="lien_next bouton"><a title="' + title + '" href="' + link + '">' + txt + '</a></div>')


@register.filter
def button_add_another_on_create(message):
    msg = str(message)
    if re.match("L'entrée de glossaire .* a été ajoutée avec succès.", msg):
        return button_new("+ entrée glossaire", "/fichier/glossaire/add/", "ajouter une entrée de glossaire")
    if re.match("La fiche .* a été ajoutée avec succès.", msg):
        return button_new("+ fiche", "/fichier/fiche/add/", "ajouter une fiche")
    if re.match("L'entrée d'agenda .* a été ajoutée avec succès.", msg):
        return button_new("+ entrée agenda", "/fichier/agenda/add/", "ajouter une entrée de l'agenda")
    else:
        return ""


@register.simple_tag
def index_alpha(key_alpha, url_key_alpha):
    result = '<div class="index_menu">'

    for letter in ascii_uppercase + "-":
        if letter == key_alpha:
            result += '<div><span class="active_visu">' + letter + "</span></div>"
        else:
            result += '<div><a class="visu" href="' + reverse(url_key_alpha, kwargs={"key": letter}) + '">' + letter + "</a></div>"

    result += "</div>"
    return mark_safe(result)

@register.simple_tag
def index_paginator(paginator, p_id, url_key_paginator):
    result = '<div class="index_menu_large">Page : '

    for id in range(1, paginator.num_pages + 1):
        sid = str(id)
        if id == p_id:
            result += '<div><span class="active_visu">' + sid + "</span></div>"
        else:
            result += '<div><a class="visu" href="' + reverse(url_key_paginator, kwargs={"key": id}) + '">' + sid + "</a></div>"

    result += "</div>"
    return mark_safe(result)
