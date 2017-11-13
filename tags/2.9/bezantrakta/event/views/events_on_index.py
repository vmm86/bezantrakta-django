from django.db.models import DateTimeField, UUIDField
from django.db.models import Case, OuterRef, Subquery, F, Q, When
from django.shortcuts import render

from project.shortcuts import timezone_now

from ..cache import get_or_set_cache as get_or_set_event_cache
from ..models import EventContainerBinder, EventGroupBinder


def events_on_index(request):
    """Вывод афиш событий в базовом шаблоне в позициях ``small_vertical``.

    Позиция афиши должна быть больше 0.
    Афиши в позиции 0 используются НЕ для вывода на главной, а для вывода событий, отфильтрованных по разным основаниям.
    """
    today = timezone_now()

    # Поиск опубликованных событий или групп на главной, привязанных к текущему домену
    group_min_datetime = EventGroupBinder.objects.values('event__datetime').filter(
        group_id=OuterRef('event_id'),
        event__is_published=True,
        event__datetime__gt=today,
    ).order_by('event__datetime')[:1]

    items_on_index = EventContainerBinder.objects.select_related(
        'event',
        'event_container',
    ).annotate(
        event_uuid=Case(
            When(event__is_group=True, then=F('event__event_group__id')),
            default=F('event__id'),
            output_field=UUIDField()
        ),
        event_datetime=Case(
            When(event__is_group=True, then=F('event__event_group__datetime')),
            default=F('event__datetime'),
            output_field=DateTimeField()
        ),
        is_group=F('event__is_group'),
        container=F('event_container__slug'),
    ).values(
        'event_uuid',
        'event_datetime',
        'is_group',
        'container',
        'order',
    ).filter(
        Q(
            Q(event__is_published=True) &
            Q(event__is_on_index=True) &
            Q(event_container__mode='small_vertical') &
            Q(order__gt=0) &
            Q(event__domain_id=request.domain_id)
        ) &
        Q(
            Q(
                Q(is_group=True) &
                Q(event_datetime=Subquery(group_min_datetime))
            ) |
            Q(
                Q(is_group=False) &
                Q(event_datetime__gt=today)
            )
        )
    ).order_by(
        'container',
        'order',
        'event_datetime',
    )

    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    small_vertical_vip = list(items_on_index.filter(container='small_vertical_vip'))
    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    small_vertical = list(items_on_index.filter(container='small_vertical'))

    for container in (small_vertical, small_vertical_vip):
        if container:
            for event in container:
                # Получение информации о каждом размещённом событии из кэша
                event_or_group = 'group' if event['is_group'] else 'event'
                event.update(get_or_set_event_cache(event['event_uuid'], event_or_group))

    context = {
        'title': '',
        'small_vertical_vip': small_vertical_vip,
        'small_vertical': small_vertical,
    }
    return render(request, 'event/events_on_index.html', context)
