import datetime

from django.contrib.humanize.templatetags.humanize import naturalday
from django.db.models import BooleanField, CharField, DateTimeField, DecimalField, IntegerField, SlugField
from django.db.models import Case, OuterRef, Subquery, F, Q, Value, When
from django.shortcuts import render

from project.shortcuts import add_small_vertical_poster

from ..models import Event, EventGroupBinder


def calendar(request, year, month, day):
    current_timezone = request.city_timezone
    calendar_date = datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day),
    )
    calendar_date_localized = current_timezone.localize(calendar_date)
    calendar_next_date = datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day) + 1,
    )
    calendar_next_date_localized = current_timezone.localize(calendar_next_date)
    range_filter = (calendar_date_localized, calendar_next_date_localized)

    group_subquery = EventGroupBinder.objects.values('event__datetime').filter(
        group=OuterRef('id'),
        event__is_published=True,
        event__datetime__range=range_filter,
    ).order_by('event__datetime')[:1]

    # Получение событий или групп в заданный день
    events_on_date = Event.objects.select_related(
        'event_venue',
        'domain'
    ).annotate(
        # Общие параметры
        is_in_group=Case(
            When(event_groups__isnull=False, then=Value(True)),
            default=False,
            output_field=BooleanField()
        ),
        # Параметры события
        event_title=Case(
            When(is_group=True, then=F('event_group__title')),
            default=F('title'),
            output_field=CharField()
        ),
        event_slug=Case(
            When(is_group=True, then=F('event_group__slug')),
            default=F('slug'),
            output_field=SlugField()
        ),
        event_datetime=Case(
            When(is_group=True, then=F('event_group__datetime')),
            default=F('datetime'),
            output_field=DateTimeField()
        ),
        event_min_price=Case(
            When(is_group=True, then=F('event_group__min_price')),
            default=F('min_price'),
            output_field=DecimalField()
        ),
        event_min_age=Case(
            When(is_group=True, then=F('event_group__min_age')),
            default=F('min_age'),
            output_field=IntegerField()
        ),
        event_venue_title=Case(
            When(is_group=True, then=F('event_group__event_venue__title')),
            default=F('event_venue__title'),
            output_field=CharField()
            ),
        # Параметры группы, если событие в неё входит
        group_slug=Case(
            When(is_group=True, then=F('slug')),
            default=None,
            output_field=SlugField()
        ),
        group_datetime=Case(
            When(is_group=True, then=F('datetime')),
            default=None,
            output_field=DateTimeField()
        ),
    ).values(
        'is_group',
        'is_in_group',
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
            Q(is_published=True) &
            Q(domain_id=request.domain_id)
        ) &
        Q(
            Q(
                Q(is_group=True) &
                Q(event_datetime=Subquery(group_subquery))
            ) |
            Q(
                (Q(is_group=False) & Q(is_in_group=False)) &
                Q(event_datetime__range=range_filter)
            )
        )
    )

    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    add_small_vertical_poster(request, events_on_date)

    context = {
        'title': 'События на {naturalday}'.format(naturalday=naturalday(calendar_date_localized)),
        'calendar_date': calendar_date_localized,
        'calendar_next_date': calendar_next_date_localized,
        'events_on_date': list(events_on_date),
    }

    return render(request, 'event/calendar.html', context)
