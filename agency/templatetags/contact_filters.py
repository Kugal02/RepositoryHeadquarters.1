from django import template

register = template.Library()

@register.filter
def contact_type_display(value):
    if not isinstance(value, str):
        return value
    return value.replace('_', ' ').title()
