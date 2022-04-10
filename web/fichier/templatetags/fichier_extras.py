from django import template
from django.utils.safestring import mark_safe
from fichier.models import Categorie, Niveau, EntreeGlossaire, EntreeAgenda
import re
from fichier.utils import Agenda
from django.urls import reverse
from datetime import datetime

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


@register.simple_tag
def lien_jour_suivant(day):
    if isinstance(day, EntreeAgenda):
        url = get_url_jour(day.date)
        text = get_day_name(day.date)
        classname = ""
    else:
        url = get_url_jour_missing(day)
        text = get_day_name(day)
        classname = " missing-day"
    return lien_jour(url, "◂ " + text, "lien_pred" + classname)


@register.simple_tag
def lien_jour_precedent(day):
    if isinstance(day, EntreeAgenda):
        url = get_url_jour(day.date)
        text = get_day_name(day.date)
        classname = ""
    else:
        url = get_url_jour_missing(day)
        text = get_day_name(day)
        classname = " missing-day"

    return lien_jour(url, text + " ▸", "lien_next" + classname)


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

    for e in EntreeGlossaire.objects.filter():
        if liens:
            result = e.ajouter_liens(result)
        else:
            result = e.ajouter_span(result)

    if liens:
        result = re.sub(r'\[([^\]<>]*)\]', r'<a class="glossaire-creer" title="ajouter « \1 » au glossaire" href="/fichier/glossaire/add/?entree=\1">\1</a>', result)
    else:
        result = re.sub(r'\[([^\]<>]*)\]', r'<span class="glossaire-creer">\1</a>', result)

    return result
