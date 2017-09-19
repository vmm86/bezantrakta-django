import datetime

from django.shortcuts import render

from project.shortcuts import add_small_vertical_poster

from ..models import Event


def category(request, slug):
    """
    Вывод событий, принадлежащих какой-либо категории событий.
    """
    today = datetime.datetime.today()
    # Фильтр событий в категориях
    category_events_filter = {}
    category_events_filter['is_published'] = True
    category_events_filter['date__gt'] = today
    category_events_filter['domain_id'] = request.domain_id
    category_events_filter['event_category__is_published'] = True
    if slug == 'vse':
        category_events_filter['event_category__isnull'] = False
    else:
        category_events_filter['event_category__slug'] = slug

    # Запрос событий из любой категории или какой-либо конкретной
    category_events = Event.objects.select_related(
        'event_category',
        'event_venue',
        'domain'
    ).filter(**category_events_filter).values(
        'title',
        'slug',
        'date',
        'time',
        'min_price',
        'min_age',
        'event_venue__title',
    )

    add_small_vertical_poster(request, category_events)

    context = {
        'category_events': category_events,
        'slug': slug,
    }
    return render(request, 'event/category.html', context)
