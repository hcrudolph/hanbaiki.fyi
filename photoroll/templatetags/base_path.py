from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name="base_path")
def base_path(value, item=1):
    return value.split('/')[item]