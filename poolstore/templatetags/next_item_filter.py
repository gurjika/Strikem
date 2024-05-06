from django import template

register = template.Library()

@register.filter
def next(loop_list, index):
    try:
        return loop_list[int(index) + 1]
    except IndexError:
        return None
    

@register.filter(name='calculate_index')
def calculate_index(page_num, loop_index):
    index = (page_num) * 10 + loop_index
    return index