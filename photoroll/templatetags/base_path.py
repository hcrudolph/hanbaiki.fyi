from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name="base_path")
@stringfilter
def base_path(value):
    return value.split('/')[1]