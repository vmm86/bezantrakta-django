from django.conf import settings
from django.db.models import F
from django.shortcuts import render
from django.utils import timezone

from project.shortcuts import add_small_vertical_poster

from ..models import Event


today = timezone.now()


def category(request, slug):
    """
    Вывод событий, принадлежащих какой-либо категории событий.
    """
    # Создание фильтра событий в категориях
    category_events_filter = {}
    category_events_filter['is_published'] = True
    category_events_filter['datetime__gt'] = today
    category_events_filter['domain_id'] = request.domain_id
    category_events_filter['event_category__is_published'] = True
    # Запрос событий из всех категорий или из какой-либо конкретной
    if slug == settings.BEZANTRAKTA_CATEGORY_ALL:
        category_events_filter['event_category__isnull'] = False
    else:
        category_events_filter['event_category__slug'] = slug

    category_events = Event.objects.select_related(
        'event_category',
        'event_venue',
        'domain'
    ).annotate(
        venue=F('event_venue__title'),
    ).filter(**category_events_filter).values(
        'title',
        'slug',
        'datetime',
        'min_price',
        'min_age',
        'venue',
    )

    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    add_small_vertical_poster(request, category_events)

    context = {
        'category_events': category_events,
        'slug': slug,
    }
    return render(request, 'event/category.html', context)
