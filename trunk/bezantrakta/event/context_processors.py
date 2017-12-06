from django.db.models import F

from project.cache import cache_factory
from project.shortcuts import base_template_context_processor, timezone_now

from .models import EventCategory, EventContainerBinder


def big_containers(request):
    """Получение событий и их добавление в контекст шаблона."""
    if base_template_context_processor(request):
        today = timezone_now()

        events_published = EventContainerBinder.objects.select_related(
            'event',
            'event_container',
        ).annotate(
            uuid=F('event__id'),
            datetime=F('event__datetime'),
            is_group=F('event__is_group'),
            container=F('event_container__slug'),
            container_mode=F('event_container__mode')
        ).values(
            'uuid',
            'datetime',
            'is_group',
            'container',
            'order',
            'img',
        ).filter(
            container_mode__startswith='big_',
            event__is_published=True,
            # datetime__gt=today,
            event__domain_id=request.domain_id,
        ).order_by(
            'container',
            'order',
            'datetime',
        )

        big_vertical_left = list(events_published.filter(container='big_vertical_left'))
        big_vertical_right = list(events_published.filter(container='big_vertical_right'))
        big_horizontal = list(events_published.filter(container='big_horizontal'))

        for container in (big_vertical_left, big_vertical_right, big_horizontal):
            if container:
                for item in container:
                    # Получение информации о каждом размещённом событии из кэша
                    item_cache = (
                        cache_factory('group', item['uuid']) if
                        item['is_group'] else
                        cache_factory('event', item['uuid'])
                    )
                    item.update(item_cache)
            # Удаляем из списка группы без актуальных на данный момент событий
            container[:] = [i for i in container if i['event_datetime'] >= today and (not i['is_group'] or (i['is_group'] and i['earliest_published_event_in_group']))]

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
