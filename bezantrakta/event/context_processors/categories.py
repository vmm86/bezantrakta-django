from django.conf import settings

from project.shortcuts import base_template_context_processor, timezone_now

from ..models import EventCategory


def categories(request):
    """Получение категорий событий и их добавление в контекст шаблона."""
    if base_template_context_processor(request):
        today = timezone_now()

        # Получение опубликованных категорий, у которых есть связанные предстоящие события
        categories = EventCategory.objects.filter(
            is_published=True,
            event__is_published=True,
            event__datetime__gt=today,
            event__domain_id=request.domain_id
        ).values(
            'title',
            'slug',
        ).distinct()

        # Пункт "Все категории"
        category_all = {}
        category_all['title'] = settings.BEZANTRAKTA_CATEGORY_ALL_TITLE
        category_all['slug'] = settings.BEZANTRAKTA_CATEGORY_ALL_SLUG
        cat_all = []
        cat_all.append(category_all)

        # Объединение "Все категории" и отдельных категорий
        from itertools import chain
        categories = list(chain(cat_all, categories))

        return {
            'categories': categories,
        }
    else:
        return {}
