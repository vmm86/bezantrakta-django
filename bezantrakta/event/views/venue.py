from django.db.models import F, Q
from django.shortcuts import redirect, render

from project.cache import cache_factory
from project.shortcuts import timezone_now

from ..models import Event, EventVenue


def venue(request, slug):
    """Фильтр событий, принадлежащих какому-либо залу (каждой из его схем) и вывод их афиш в позиции ``small_vertical``.

    Args:
        slug (str): Псевдоним зала.
    """
    today = timezone_now()

    # Получение названия зала из БД
    try:
        venue_title = EventVenue.objects.values_list('title', flat=True).get(slug=slug)
    # Если зал не существует в БД - редирект на главную
    except EventVenue.DoesNotExist:
        return redirect('/')

    # Запрос событий из всех категорий или из какой-либо конкретной
    venue_events = list(Event.objects.select_related(
        'event_venue',
        'domain'
    ).annotate(
        uuid=F('id'),
    ).values(
        'uuid',
    ).filter(
        Q(is_group=False) &
        Q(is_published=True) &
        Q(datetime__gt=today) &
        Q(event_venue__slug=slug) &
        Q(domain_id=request.domain_id)
    ).order_by(
        'datetime',
        'title'
    ))

    if venue_events:
        for event in venue_events:
            # Получение информации о каждом размещённом событии из кэша
            event.update(cache_factory('event', event['uuid']))

    context = {
        'title': venue_title,
        'slug': slug,
        'venue_events': venue_events,
    }
    return render(request, 'event/venue.html', context)
