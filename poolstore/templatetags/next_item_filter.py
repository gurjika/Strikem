from django import template

register = template.Library()

@register.filter
def return_next(loop_list, index):
    try:
        return list[index + 1]
    except IndexError:
        return None