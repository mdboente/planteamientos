from django import template


register = template.Library()


@register.filter()
def sum_list(value, parm):
    lista = [parm]
    return lista + value
