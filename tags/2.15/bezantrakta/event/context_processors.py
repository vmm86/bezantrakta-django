from django.db.models import DateTimeField, UUIDField
from django.db.models import Case, OuterRef, Subquery, F, Q, When

from project.shortcuts import base_template_context_processor, timezone_now

from .cache import event_or_group_cache
from .models import EventCategory, EventContainerBinder, EventGroupBinder


def big_containers(request):
    """Получение событий и их добавление в контекст шаблона."""
    if base_template_context_processor(request):
        today = timezone_now()

        # Поиск опубликованных событий на главной, привязанных к текущему домену
        group_min_datetime = EventGroupBinder.objects.values('event__datetime').filter(
            group_id=OuterRef('event__id'),
            event__is_published=True,
            event__datetime__gt=today,
        ).order_by('event__datetime')[:1]

        events_published = EventContainerBinder.objects.select_related(
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
            container_mode=F('event_container__mode')
        ).values(
            'event_uuid',
            'event_datetime',
            'is_group',
            'container',
            'order',
            'img',
        ).filter(
            Q(event__is_published=True) &
            Q(container_mode__startswith='big_') &
            Q(event__domain_id=request.domain_id) &
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

        big_vertical_left = list(events_published.filter(container='big_vertical_left'))
        big_vertical_right = list(events_published.filter(container='big_vertical_right'))
        big_horizontal = list(events_published.filter(container='big_horizontal'))

        for container in (big_vertical_left, big_vertical_right, big_horizontal):
            if container:
                for event in container:
                    # Получение информации о каждом размещённом событии из кэша
                    event_cache = event_or_group_cache(event['event_uuid'], 'event')
                    event.update(event_cache)

        return {
            'big_vertical_left':  big_vertical_left,
            'big_vertical_right': big_vertical_right,
            'big_horizontal':     big_horizontal,
        }
    else:
        return {}


def categories(request):
    """Получение категорий событий и их добавление в контекст шаблона."""
    if base_template_context_processor(request):
        today = timezone_now()

        # Получение опубликованных категорий, у которых есть связанные предстоящие события
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
        cat_all = []
        cat_all.append(category_all)

        # Объединение "Все категории" и отдельных категорий
        from itertools import chain
        categories = list(chain(cat_all, categories))

        return {
            'categories': categories,
        }
    else:
        return {}
