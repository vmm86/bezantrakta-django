from .models import Menu, MenuItem


def menu_items(request):
    """
    Context processor that adds `menu` information to template context.
    """
    menu = {
        menu['slug']: menu['title']
        for menu
        in Menu.objects.values('slug', 'title')
    }

    menu_items = {}
    for slug, title in menu.items():
        menu_items[slug] = MenuItem.objects.filter(
            menu__slug=slug,
            domain__slug=request.domain,
        ).values('title', 'slug', 'is_published')

    return {
        'menu': menu,
        'menu_items': menu_items,
    }
