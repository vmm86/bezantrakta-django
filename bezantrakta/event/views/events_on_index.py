from django.db.models import F
from django.shortcuts import render
from django.utils import timezone

from project.shortcuts import add_small_vertical_poster

from ..models import EventContainerBinder


today = timezone.now()


def events_on_index(request):
    # Поиск опубликованных событий на главной, привязанных к текущему домену
    events_on_index = EventContainerBinder.objects.select_related(
        'event',
        'event_container',
        'event_venue',
        'domain',
    ).annotate(
        title=F('event__title'),
        slug=F('event__slug'),
        datetime=F('event__datetime'),
        min_price=F('event__min_price'),
        min_age=F('event__min_age'),
        venue=F('event__event_venue__title'),
    ).values(
        'title',
        'slug',
        'datetime',
        'min_price',
        'min_age',
        'venue',
    ).filter(
        event__is_published=True,
        event__is_on_index=True,
        event__datetime__gt=today,
        event__domain_id=request.domain_id,
    )

    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    small_vertical_vip = events_on_index.filter(event_container__slug='small_vertical_vip')
    add_small_vertical_poster(request, small_vertical_vip)
    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    small_vertical = events_on_index.filter(event_container__slug='small_vertical')
    add_small_vertical_poster(request, small_vertical)

    context = {
        'small_vertical_vip': small_vertical_vip,
        'small_vertical': small_vertical,
    }
    return render(request, 'event/events_on_index.html', context)
