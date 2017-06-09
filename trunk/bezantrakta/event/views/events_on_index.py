import datetime

from django.db.models import F
from django.shortcuts import render

from project.shortcuts import add_small_vertical_poster

from ..models import Event


def events_on_index(request):
    # Поиск опубликованных событий на главной, привязанных к текущему домену
    today = datetime.datetime.today()

    events_on_index = Event.objects.select_related(
        'event_venue',
        'domain'
    ).annotate(
        venue=F('event_venue__title'),
    ).filter(
        is_published=True,
        is_on_index=True,
        date__gt=today,
        domain_id=request.domain_id
    ).values(
        'title',
        'slug',
        'date',
        'time',
        'min_price',
        'min_age',
        'venue',
    )

    add_small_vertical_poster(request, events_on_index)

    context = {
        'events_on_index': events_on_index,
    }
    return render(request, 'event/events_on_index.html', context)
