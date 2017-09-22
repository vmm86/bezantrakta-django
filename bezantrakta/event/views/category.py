from django.conf import settings
from django.db.models import F, Q
from django.shortcuts import render

from project.shortcuts import timezone_now

from ..models import Event, EventCategory
from ..shortcuts import add_small_vertical_poster


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
    category_events = Event.objects.select_related(
        'event_category',
        'event_venue',
        'domain'
    ).annotate(
        event_title=F('title'),
        event_slug=F('slug'),
        event_datetime=F('datetime'),
        event_min_price=F('min_price'),
        event_min_age=F('min_age'),
        event_venue_title=F('event_venue__title'),
        event_category_title=F('event_category__title'),
    ).values(
        'event_title',
        'event_slug',
        'event_datetime',
        'event_min_price',
        'event_min_age',
        'event_venue_title',
        'event_category_title',
    ).filter(
        Q(is_group=False) &
        Q(is_published=True) &
        Q(event_category__is_published=True) &
        category_event_filter &
        Q(event_datetime__gt=today) &
        Q(domain_id=request.domain_id)
    ).order_by(
        'event_datetime',
        'event_title'
    )

    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    add_small_vertical_poster(request, category_events)

    context = {
        'title': category_name,
        'slug': slug,
        'category_events': list(category_events),
    }
    return render(request, 'event/category.html', context)
