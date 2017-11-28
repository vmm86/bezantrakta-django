from django.conf import settings
from django.db.models import F, Q
from django.shortcuts import render

from project.cache import cache_factory
from project.shortcuts import timezone_now

from ..models import Event, EventCategory


def category(request, slug):
    """Фильтр событий, принадлежащих какой-либо категории и вывод их афиш в позиции ``small_vertical``.

    Args:
        slug (str): Псевдоним категории.
    """
    today = timezone_now()

    # Запрос событий из всех категорий или из какой-либо конкретной
    category_events = list(Event.objects.select_related(
        'event_category',
        'event_venue',
        'domain'
    ).annotate(
        event_uuid=F('id'),
    ).values(
        'event_uuid',
    ).filter(
        Q(is_group=False) &
        Q(is_published=True) &
        Q(datetime__gt=today) &
        Q(domain_id=request.domain_id)
    ).order_by(
        'datetime',
        'title'
    ))

    if category_events:
        for event in category_events:
            # Получение информации о каждом размещённом событии из кэша
            event.update(cache_factory('event', event['event_uuid']))

    # Получение событий во всех категориях или фильтр по конкретной категории
    if slug == settings.BEZANTRAKTA_CATEGORY_ALL:
        category_title = 'Все события'
        category_events[:] = [ce for ce in category_events if ce['event_category_slug'] is not None]
    else:
        category_title = EventCategory.objects.values_list('title', flat=True).get(slug=slug)
        category_events[:] = [ce for ce in category_events if ce['event_category_slug'] == slug]

    context = {
        'title': category_title,
        'slug': slug,
        'category_events': category_events,
    }
    return render(request, 'event/category.html', context)
