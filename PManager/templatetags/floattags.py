__author__ = 'Gvammer'
from django.template.defaultfilters import floatformat
from django.template import Library

register = Library()
@register.filter(name='dotted_float')
def dotted_float(value):
    value = floatformat(value)
    return str(value).replace(',','.')