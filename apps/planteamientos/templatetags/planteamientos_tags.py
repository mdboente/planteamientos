from django import template

register = template.Library()


@register.filter
def Si_o_No(value: bool) -> str:
    return 'Sí' if value else 'No'


@register.filter
def secretario(value):
    resp = False
    if hasattr(value, 'seccionsindical'):
        resp = True
    return resp


@register.filter()
def dic(value, indice):
    return value[indice]


@register.filter()
def ninguno(value):
    return 'No especificado ' if value is None else value


@register.filter()
def has_attr(value, relation):
    return hasattr(value, relation)
