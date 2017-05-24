from django.utils.deprecation import MiddlewareMixin

from .models import Menu


class MenuItemsMiddleware(MiddlewareMixin):
    """
    Middleware sets Menu items available from every menu on current site.
    """
    def process_request(self, request):
        if request:
            top_menu_items = Menu.objects.get(
                slug='top_menu'
            ).menuitem_set.filter(
                domain__slug=request.domain_slug,
            )
            request.top_menu_items = top_menu_items

            bottom_menu_items = Menu.objects.get(
                slug='bottom_menu'
            ).menuitem_set.filter(
                domain__slug=request.domain_slug,
            )
            request.bottom_menu_items = bottom_menu_items
