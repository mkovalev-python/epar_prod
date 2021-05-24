__author__ = 'Gvammer'
from django.template import Library

register = Library()
@register.filter(name='joinby')
def joinby(value, arg):
    return arg.join(value)

@register.filter(name='reallength')
def reallength(value):
  """Returns the length of the value - useful for lists."""
  try:
     value.count()
  except:
     return len(value)