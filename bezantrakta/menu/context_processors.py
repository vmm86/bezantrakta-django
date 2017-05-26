from .models import MenuItem


def menu_items(request):
    """
    Context processor that adds `menu` information to template context.
    """
    top_menu_items = MenuItem.objects.only(
        'title', 'slug', 'is_published'
    ).filter(
        menu__slug='top_menu',
        domain__slug=request.domain,
    )

    bottom_menu_items = MenuItem.objects.only(
        'title', 'slug', 'is_published'
    ).filter(
        menu__slug='bottom_menu',
        domain__slug=request.domain,
    )

    return {
        'top_menu_items': top_menu_items,
        'bottom_menu_items': bottom_menu_items
    }
