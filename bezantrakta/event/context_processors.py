from django.db.models import F
from django.utils import timezone

from .models import Event, EventCategory, EventContainerBinder


today = timezone.now()


def big_containers(request):
    """
    Получение событий и их добавление в template context.
    """
    # Только если домен опубликован
    if request.domain_is_published:
        # Поиск опубликованных событий на главной, привязанных к текущему домену
        events_published = EventContainerBinder.objects.select_related(
            'event_container',
            'event',
        ).annotate(
            title=F('event__title'),
            slug=F('event__slug'),
            datetime=F('event__datetime'),
            timezone=F('event__domain__city__timezone'),
            min_price=F('event__min_price'),
            min_age=F('event__min_age'),
            venue=F('event__event_venue__title'),
            container=F('event_container__slug'),
        ).filter(
            event__is_published=True,
            event__datetime__gt=today,
            event__domain_id=request.domain_id
        ).values(
            'title',
            'slug',
            'datetime',
            'timezone',
            'min_price',
            'min_age',
            'venue',
            'img',
            'container'
        )

        big_vertical_left = events_published.filter(
            event_container__slug='big_vertical_left',
        )
        big_vertical_right = events_published.filter(
            event_container__slug='big_vertical_right',
        )
        big_horizontal = events_published.filter(
            event_container__slug='big_horizontal',
        )

        return {
            'big_vertical_left': big_vertical_left,
            'big_vertical_right': big_vertical_right,
            'big_horizontal': big_horizontal,
        }
    else:
        return {}


def categories(request):
    """
    Получение категорий событий и их добавление в template context.
    """
    # Только если домен опубликован
    if request.domain_is_published:
        # Получение опубликованных категорий, у которых есть связанные предстоящие события
        # .annotate(event_count=Count('event'))
        categories = EventCategory.objects.filter(
            is_published=True,
            event__is_published=True,
            event__datetime__gt=today,
            event__domain_id=request.domain_id
        ).values(
            'title',
            'slug',
        ).distinct()

        # Пункт "Все категории"
        category_all = {}
        category_all['title'] = 'Все события'
        category_all['slug'] = 'vse'
        category_all['event_count'] = Event.objects.filter(
            is_published=True,
            datetime__gt=today,
            domain_id=request.domain_id,
        ).count()
        cat_all = []
        cat_all.append(category_all)

        # Объединение "Все категории" и отдельных категорий
        from itertools import chain
        categories = list(chain(cat_all, categories))

        return {
            'today': today,
            'categories': categories,
        }
    else:
        return {}
