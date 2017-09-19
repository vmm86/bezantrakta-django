from django.db.models import CharField, DateTimeField, DecimalField, IntegerField, SlugField
from django.db.models import Case, OuterRef, Subquery, F, Q, When

from project.shortcuts import base_template_context_processor, timezone_now

from .models import EventCategory, EventContainerBinder, EventGroupBinder


def big_containers(request):
    """
    Получение событий и их добавление в template context.
    """
    if base_template_context_processor(request):
        today = timezone_now()

        # Поиск опубликованных событий на главной, привязанных к текущему домену
        group_min_datetime = EventGroupBinder.objects.values('event__datetime').filter(
            group_id=OuterRef('event__id'),
            # event__is_published=True,
            event__datetime__gt=today,
        ).order_by('event__datetime')[:1]

        events_published = EventContainerBinder.objects.select_related(
            'event_container',
            'event',
        ).annotate(
            # Общие параметры
            is_group=F('event__is_group'),
            container=F('event_container__slug'),
            # Параметры события
            event_title=Case(
                When(event__is_group=True, then=F('event__event_group__title')),
                default=F('event__title'),
                output_field=CharField()
            ),
            event_slug=Case(
                When(event__is_group=True, then=F('event__event_group__slug')),
                default=F('event__slug'),
                output_field=SlugField()
            ),
            group_slug=Case(
                When(event__is_group=True, then=F('event__slug')),
                default=None,
                output_field=SlugField()
            ),
            event_datetime=Case(
                When(event__is_group=True, then=F('event__event_group__datetime')),
                default=F('event__datetime'),
                output_field=DateTimeField()
            ),
            group_datetime=Case(
                When(event__is_group=True, then=F('event__datetime')),
                default=None,
                output_field=DateTimeField()
            ),
            event_min_price=Case(
                When(event__is_group=True, then=F('event__event_group__min_price')),
                default=F('event__min_price'),
                output_field=DecimalField()
            ),
            event_min_age=Case(
                When(event__is_group=True, then=F('event__event_group__min_age')),
                default=F('event__min_age'),
                output_field=IntegerField()
            ),
            event_venue_title=Case(
                When(event__is_group=True, then=F('event__event_group__event_venue__title')),
                default=F('event__event_venue__title'),
                output_field=CharField()
            ),
        ).values(
            'is_group',
            'container',
            'event_title',
            'event_slug',
            'event_datetime',
            'event_min_price',
            'event_min_age',
            'event_venue_title',
            'img',
        ).filter(
            Q(
                Q(event__is_published=True) &
                # Q(event__is_on_index=True) &
                (Q(event_container__mode='big_vertical') | Q(event_container__mode='big_horizontal')) &
                Q(event__domain_id=request.domain_id)
            ) &
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
        )

        big_vertical_left = list(events_published.filter(
            container='big_vertical_left',
        ))
        big_vertical_right = list(events_published.filter(
            container='big_vertical_right',
        ))
        big_horizontal = list(events_published.filter(
            container='big_horizontal',
        ))

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
