from django import template
import re

register = template.Library()

@register.filter
def get_form_field(form, field_name):
    return form[field_name]

@register.filter(name='add_class')
def add_class(field, css_class):
    try:
        return field.as_widget(attrs={"class": css_class})
    except AttributeError:
        return field  # fallback if it's a string

@register.filter(name='phone_format')
def phone_format(value):
    """Format phone numbers to XXX-XXX-XXXX"""
    cleaned = re.sub(r'\D', '', str(value))
    if len(cleaned) == 10:
        return f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
    return value
