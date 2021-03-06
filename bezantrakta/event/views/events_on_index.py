from operator import itemgetter

from django.db.models import F
from django.shortcuts import render

from project.cache import cache_factory
from project.shortcuts import timezone_now

from ..models import EventContainerBinder
from ..shortcuts import hide_test_events_in_production


def events_on_index(request):
    """Вывод афиш событий в базовом шаблоне в позициях ``small_vertical``.

    Позиция афиши должна быть больше 0.
    Афиши в позиции 0 используются НЕ для вывода на главной, а для вывода событий, отфильтрованных по разным основаниям.
    """
    today = timezone_now()

    items_on_index = EventContainerBinder.objects.select_related(
        'event',
        'event_container',
    ).annotate(
        uuid=F('event__id'),
        datetime=F('event__datetime'),
        is_group=F('event__is_group'),
        container=F('event_container__slug'),
        container_mode=F('event_container__mode'),
    ).values(
        'uuid',
        'is_group',
        'container',
        'order',
    ).filter(
        container_mode='small_vertical',
        event__is_published=True,
        event__is_on_index=True,
        datetime__gt=today,
        event__domain_id=request.domain_id,
    ).order_by(
        'container',
        'order',
        'datetime',
    )

    small_vertical_vip = list(items_on_index.filter(container='small_vertical_vip'))
    small_vertical = list(items_on_index.filter(container='small_vertical'))

    for container in (small_vertical, small_vertical_vip):
        if container:
            for item in container:
                # Получение информации о каждом размещённом событии/группе из кэша
                item_cache = (
                    cache_factory('group', item['uuid']) if
                    item['is_group'] else
                    cache_factory('event', item['uuid'])
                )
                item.update(item_cache)
            # Оставляем в списке ВСЕ актуальные события и удаляем группы БЕЗ актуальных на данный момент событий
            container[:] = [
                i for i in container if
                i['event_datetime'] >= today and
                (not i['is_group'] or (i['is_group'] and i['earliest_published_event_in_group'])) and
                hide_test_events_in_production(i)
            ]
            container = sorted(container, key=itemgetter('event_datetime'))

    context = {
        'title': '',
        'small_vertical_vip': small_vertical_vip,
        'small_vertical': small_vertical,
    }
    return render(request, 'event/events_on_index.html', context)
