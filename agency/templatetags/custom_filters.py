from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """
    Custom template filter to get a dictionary value by key.
    Usage: {{ some_dict|dict_get:some_key }}
    """
    return d.get(key) if d else None
