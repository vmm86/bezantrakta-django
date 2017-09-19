from django.db.models import CharField, DateTimeField, DecimalField, IntegerField, SlugField
from django.db.models import Case, OuterRef, Subquery, F, Q, When
from django.shortcuts import render

from project.shortcuts import timezone_now

from ..models import EventContainerBinder, EventGroupBinder
from ..shortcuts import add_small_vertical_poster


def events_on_index(request):
    """Вывод событий в базовом шаблоне в позициях ``small_vertical``."""
    today = timezone_now()

    # Поиск опубликованных событий или групп на главной, привязанных к текущему домену
    group_min_datetime = EventGroupBinder.objects.values('event__datetime').filter(
        group_id=OuterRef('event__id'),
        # event__is_published=True,
        event__datetime__gt=today,
    ).order_by('event__datetime')[:1]

    items_on_index = EventContainerBinder.objects.select_related(
        'event',
        'event_container',
    ).annotate(
        # Общие параметры
        is_group=F('event__is_group'),
        container=F('event_container__slug'),
        # Параметры события
        event_title=Case(
            When(event__is_group=True, then=F('event__event_group__title')),
            default=F('event__title'),
            output_field=CharField()
        ),
        event_slug=Case(
            When(event__is_group=True, then=F('event__event_group__slug')),
            default=F('event__slug'),
            output_field=SlugField()
        ),
        event_datetime=Case(
            When(event__is_group=True, then=F('event__event_group__datetime')),
            default=F('event__datetime'),
            output_field=DateTimeField()
        ),
        event_min_price=Case(
            When(event__is_group=True, then=F('event__event_group__min_price')),
            default=F('event__min_price'),
            output_field=DecimalField()
        ),
        event_min_age=Case(
            When(event__is_group=True, then=F('event__event_group__min_age')),
            default=F('event__min_age'),
            output_field=IntegerField()
        ),
        event_venue_title=Case(
            When(event__is_group=True, then=F('event__event_group__event_venue__title')),
            default=F('event__event_venue__title'),
            output_field=CharField()
        ),
        # Параметры группы, если событие в неё входит
        group_slug=Case(
            When(event__is_group=True, then=F('event__slug')),
            default=None,
            output_field=SlugField()
        ),
        group_datetime=Case(
            When(event__is_group=True, then=F('event__datetime')),
            default=None,
            output_field=DateTimeField()
        ),
    ).values(
        'is_group',
        'container',
        'order',
        'event_title',
        'event_slug',
        'group_slug',
        'event_datetime',
        'group_datetime',
        'event_min_price',
        'event_min_age',
        'event_venue_title',
    ).filter(
        Q(
            Q(event__is_published=True) &
            Q(event__is_on_index=True) &
            Q(event_container__mode='small_vertical') &
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
    add_small_vertical_poster(request, small_vertical_vip)
    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    small_vertical = list(items_on_index.filter(container='small_vertical'))
    add_small_vertical_poster(request, small_vertical)

    context = {
        'title': '',
        'small_vertical_vip': small_vertical_vip,
        'small_vertical': small_vertical,
    }
    return render(request, 'event/events_on_index.html', context)
