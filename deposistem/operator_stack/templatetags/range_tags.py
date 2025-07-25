from django import template

register = template.Library()

@register.filter
def make_list(start, count):
    return list(range(start, start + count))

@register.filter
def get(dictionary, key):
    return dictionary.get(key)