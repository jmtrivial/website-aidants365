from django import template

register = template.Library()


@register.filter
def nomenclature(value):
    return str(value)


@register.filter
def number_xxxx(value):
    return "{:04d}".format(value)


@register.filter
def affiche_si_existe(value, arg):
    if value:
        return "<strong>" + arg + "&nbsp;:</strong> " + value
    else:
        return ""


@register.simple_tag
def affiche_bloc_si_existe(value, name1, name2):
    if value:
        if name2:
            return "<p><strong>" + name1 + " " + name2 + "&nbsp;:</strong> " + value + "</p>";
        else:
            return "<p><strong>" + name1 + "&nbsp;:</strong> " + value + "</p>";
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
