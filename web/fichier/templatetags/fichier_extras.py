from django import template
from django.utils.safestring import mark_safe
from fichier.models import Categorie, Niveau, EntreeGlossaire, EntreeAgenda, EntetePage, Ephemeride
import re
from fichier.utils import Agenda
from django.urls import reverse
from datetime import datetime, date
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
def carre_colore_from_applicablilite(app):
    value = Niveau.Applicabilite.couleur(app)
    return mark_safe("<div class=\"carre\" style=\"background-color: " + value + "\"> </div>")


@register.filter
def nom_from_applicablilite(app):
    return Niveau.Applicabilite.nom(app)


@register.filter
def number_xxxx(value):
    return "{:04d}".format(value)


@register.filter
def nom_mois(value):
    return Agenda.month_name[value].lower()


@register.filter
def two_chars(nb):
    if nb < 10:
        return "0" + str(nb)
    else:
        return nb


@register.filter
def nom_mois_particule(value):
    n = Agenda.month_name[value].lower()
    if n[0] in ['a', 'e', 'i', 'o', 'u']:
        return "d'" + n
    else:
        return "de " + n


@register.simple_tag
def show_year(agenda, year):
    return mark_safe(agenda.year(year))


@register.simple_tag
def show_month(agenda, year, month, simple=False, current=None):
    return mark_safe(agenda.month(year, month, simple, current))


def get_url_jour_missing(d):
    return reverse("fichier:object_add", kwargs={"classname": "agenda"}) + "?date=" + str(d.day) + "/" + str(d.month) + "/" + str(d.year)


def get_url_jour(d):
    return reverse("fichier:entree_agenda", kwargs={"year": d.year, "month": d.month, "day": d.day})


def get_day_name(d):
    return str(d.day) + " " + Agenda.month_name[d.month].lower() + " " + str(d.year)


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
def lien_mois_precedent(year, month, details):
    month -= 1
    if month == 0:
        year -= 1
        month = 12
    return mark_safe('<a class="lien_pred" href="' + reverse("fichier:agenda_month" + ("_details" if details == 1 else ""), kwargs={"year": year, "month": month}) + '">◂ ' + Agenda.month_name[month] + " " + str(year) + "</a>")


@register.simple_tag
def lien_mois_suivant(year, month, details):
    month += 1
    if month == 13:
        year += 1
        month = 1
    return mark_safe('<a class="lien_next" href="' + reverse("fichier:agenda_month" + ("_details" if details == 1 else ""), kwargs={"year": year, "month": month}) + '">' + Agenda.month_name[month] + " " + str(year) + " ▸</a>")


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
    pat1 = re.compile(r"(^|\<p\>|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
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
def index_paginator(paginator, p_id, url_key_paginator, classname=""):
    result = '<div class="index_menu_large">Page : '

    for id in range(1, paginator.num_pages + 1):
        sid = str(id)
        if id == p_id:
            result += '<div><span class="active_visu">' + sid + "</span></div>"
        elif classname == "":
            result += '<div><a class="visu" href="' + reverse(url_key_paginator, kwargs={"key": id}) + '">' + sid + "</a></div>"
        else:
            result += '<div><a class="visu" href="' + reverse(url_key_paginator, kwargs={"key": id, "classname": classname}) + '">' + sid + "</a></div>"

    result += "</div>"
    return mark_safe(result)


@register.simple_tag
def url_entete_edit(entete):
    if isinstance(entete, str):
        return EntetePage.create_url(entete)
    else:
        return entete.edit_url()


@register.simple_tag
def entete_texte(entete):
    default_message = "<p><em>Entête non définie.</em></p>"
    if isinstance(entete, str):
        return mark_safe(default_message)
    else:
        txt = entete.texte
        if txt == "":
            return mark_safe(default_message)
        else:
            return mark_safe(entete.texte)


@register.filter
def niveau_suivant(niveau):
    return niveau[0] + str(int(niveau[1]) + 1)


@register.filter
def is_recent_entry(d):
    return d > datetime.fromisoformat('2022-10-08T19:15+02:00')


@register.filter
def is_recent_entry_2(d):
    return d > datetime.fromisoformat('2022-12-09T19:08+01:00')


@register.filter
def is_ephemeride(obj):
    return isinstance(obj, Ephemeride)


@register.filter
def get_month_absolute_url(month):
    if isinstance(month, str):
        return reverse("fichier:agenda_month", args=[int(x) for x in month.split("/")[1:3]])
    else:
        return month.get_absolute_url()
