from .models import Menu, MenuItem


def menu_items(request):
    """
    Context processor that adds `menu` information to template context.
    """
    menu_values = Menu.objects.values('id', 'slug', 'title')

    menu = {
        m['slug']: m['title']
        for m
        in menu_values
    }

    menu_items = {}
    for m in menu_values:
        menu_items[m['slug']] = MenuItem.objects.filter(
            menu_id=m['id'],
            is_published=True,
            domain_id=request.domain_id,
        ).values('title', 'slug')

    return {
        'menu': menu,
        'menu_items': menu_items,
    }
