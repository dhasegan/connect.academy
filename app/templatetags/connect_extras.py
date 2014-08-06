from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='safewrap')
@stringfilter
def safewrap(value, arg):
    return value.format( arg )
safewrap.is_safe=True