from django.db.models import Case, F, URLField, Value, When
from django.db.models.functions.base import Concat

from .models import Menu, MenuItem


def menu_items(request):
    """
    Получение информации о меню и её добавление в template context.
    """
    # Только если домен опубликован
    if request.domain_is_published:
        menu_values = Menu.objects.values('id', 'slug', 'title')

        menu = {
            m['slug']: m['title']
            for m
            in menu_values
        }

        menu_items = {}
        for m in menu_values:
            menu_items[m['slug']] = MenuItem.objects.annotate(
                url=Case(
                    When(slug='', then=Value('/')),
                    default=Concat(
                        Value('/'),
                        F('slug'),
                        Value('/'),
                    ),
                    output_field=URLField()
                )
            ).filter(
                menu_id=m['id'],
                is_published=True,
                domain_id=request.domain_id,
            ).values('title', 'slug', 'url')

        return {
            'menu': menu,
            'menu_items': menu_items,
        }
    else:
        return {}
