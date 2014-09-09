from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="str", is_safe=True)
@stringfilter
def str(value):
    return value


@register.filter(name='safewrap')
@stringfilter
def safewrap(value, arg):
    """
    Filter - replaces {0} in string with input variable
    Usage (in template):

    {% with link="connect.academy" %}
    {% with link_start='<a href="{0}">'|safewrap:link %}
    Results with the variable:
    link_start = <a href="connect.academy">
    """
    return value.format(arg)
safewrap.is_safe = True


@register.filter(name="get_range", is_safe=True)
def get_range(value):
    """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
    """
    return range(value)

@register.filter(expects_localtime=True)
def short_time(value):
    return value.strftime("%H:%M")