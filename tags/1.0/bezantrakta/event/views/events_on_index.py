import datetime

from django.db.models import F
from django.shortcuts import render

from project.shortcuts import add_small_vertical_poster

from ..models import EventContainerBinder


def events_on_index(request):
    # Поиск опубликованных событий на главной, привязанных к текущему домену
    today = datetime.datetime.today()

    events_on_index = EventContainerBinder.objects.select_related(
        'event',
        'event_container',
        'event_venue',
        'domain'
    ).annotate(
        title=F('event__title'),
        slug=F('event__slug'),
        date=F('event__date'),
        time=F('event__time'),
        min_price=F('event__min_price'),
        min_age=F('event__min_age'),
        venue=F('event__event_venue__title'),
    ).values(
        'title',
        'slug',
        'date',
        'time',
        'min_price',
        'min_age',
        'venue',
    ).filter(
        event__is_published=True,
        event__is_on_index=True,
        event__date__gt=today,
        event__domain_id=request.domain_id,
    )

    small_vertical_vip = events_on_index.filter(event_container__slug='small_vertical_vip')
    add_small_vertical_poster(request, small_vertical_vip)

    small_vertical = events_on_index.filter(event_container__slug='small_vertical')
    add_small_vertical_poster(request, small_vertical)

    context = {
        'small_vertical_vip': small_vertical_vip,
        'small_vertical': small_vertical,
    }
    return render(request, 'event/events_on_index.html', context)
