from django.db.models import F

from .models import Event, EventCategory, EventContainerBinder


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
            date=F('event__date'),
            time=F('event__time'),
            min_price=F('event__min_price'),
            min_age=F('event__min_age'),
            venue=F('event__event_venue__title'),
            container=F('event_container__slug')
        ).filter(
            event__is_published=True,
            event__domain_id=request.domain_id
        ).values(
            'title',
            'slug',
            'date',
            'time',
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
        import datetime
        from django.db.models import Count

        today = datetime.datetime.today()

        # Получение опубликованных категорий, у которых есть связанные предстоящие события
        categories = EventCategory.objects.filter(
            is_published=True,
            event__is_published=True,
            event__date__gt=today,
            event__domain_id=request.domain_id
        ).annotate(
            event_count=Count('event')
        ).values(
            'title',
            'slug',
            'event_count'
        ).distinct()

        # Пункт "Все категории"
        category_all = {}
        category_all['title'] = 'Все события'
        category_all['slug'] = 'vse'
        category_all['event_count'] = Event.objects.filter(
            is_published=True,
            date__gt=today,
            domain_id=request.domain_id,
        ).count()
        cat_all = []
        cat_all.append(category_all)

        # Объединение "Все категории" и отдельных категорий
        from itertools import chain
        categories = list(chain(cat_all, categories))

        return {
            'categories': categories
        }
    else:
        return {}
