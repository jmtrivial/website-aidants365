from django import template
from django.utils.safestring import mark_safe
from fichier.models import Categorie, Niveau, EntreeGlossaire
import re

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


@register.filter
def ajouter_glossaire(texte):
    result = texte

    for e in EntreeGlossaire.objects.filter():
        result = e.ajouter_liens(result)

    result = re.sub(r'\[([^\]<>]*)\]', r'<a class="glossaire-creer" title="ajouter « \1 » au glossaire" href="/admin/fichier/entreeglossaire/add/?entree=\1">\1</a>', result)

    return result


@register.filter
def highlight_search(text, search):
    if search:
        return text.replace(search.translate(table), '<span class="highlight">' + search.translate(table) + '</span>')
    else:
        return text
