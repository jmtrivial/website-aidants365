from django import template
from django.utils.safestring import mark_safe
from fichier.models import Categorie, Niveau

register = template.Library()


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
