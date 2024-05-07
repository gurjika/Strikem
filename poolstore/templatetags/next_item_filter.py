from django import template

register = template.Library()

@register.filter
def next(loop_list, index):
    try:
        return loop_list[int(index) + 1]
    except IndexError:
        return None
    

@register.filter(name='show_username')
def show_username(paginator, page_obj):
    if page_obj.has_previous():
        previous_page_obj = paginator.get_page(page_obj.number - 1)
        messages_to_display = list(page_obj)[::-1]
        messages_displayed = list(previous_page_obj)[::-1]
        if messages_displayed[0].sender != messages_to_display[-1].sender:
            return True
        return False
    
    return True
    

