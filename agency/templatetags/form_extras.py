from django import template

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
