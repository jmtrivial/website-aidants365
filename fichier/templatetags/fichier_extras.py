from django import template

register = template.Library()

@register.filter
def nomenclature(value):
    return str(value)

@register.filter
def affiche_si_existe(value, arg):
    if value:
        return "<strong>" + arg + "&nbsp;:</strong> " + value
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


