from django.conf import settings
from django.db.models import F, Q
from django.shortcuts import render

from project.shortcuts import timezone_now

from ..cache import get_or_set_cache as get_or_set_event_cache
from ..models import Event, EventCategory


def category(request, slug):
    """Фильтр событий, принадлежащих какой-либо категории и вывод их афиш в позиции ``small_vertical``.

    Args:
        slug (str): Псевдоним категории.
    """
    today = timezone_now()

    # Получение событий во всех категориях или фильтр по конкретной категории
    if slug == settings.BEZANTRAKTA_CATEGORY_ALL:
        category_name = 'Все события'
        category_event_filter = Q(event_category__isnull=False)
    else:
        category_name = EventCategory.objects.values_list('title', flat=True).get(slug=slug)
        category_event_filter = Q(event_category__slug=slug)

    # Запрос событий из всех категорий или из какой-либо конкретной
    category_events = list(Event.objects.select_related(
        'event_category',
        'event_venue',
        'domain'
    ).annotate(
        uuid=F('id'),
        category_title=F('event_category__title'),
    ).values(
        'uuid',
        'category_title',
    ).filter(
        Q(is_group=False) &
        Q(is_published=True) &
        Q(event_category__is_published=True) &
        category_event_filter &
        Q(datetime__gt=today) &
        Q(domain_id=request.domain_id)
    ).order_by(
        'datetime',
        'title'
    ))

    if category_events:
        for event in category_events:
            # Получение информации о каждом размещённом событии из кэша
            event.update(get_or_set_event_cache(event['uuid']))

    context = {
        'title': category_name,
        'slug': slug,
        'category_events': category_events,
    }
    return render(request, 'event/category.html', context)
