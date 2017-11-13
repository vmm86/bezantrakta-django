from dateutil.parser import parse
import os
import pytz
import simplejson as json

from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.urls.base import reverse

from project.shortcuts import build_absolute_url, debug_console, json_serializer, humanize_date

from .models import Event


def get_or_set_cache(event_uuid, event_or_group, reset=False):
    """Кэширование параметров события или группы для последующего использования без запросов в БД.

    Args:
        event_uuid (UUID): Уникальный идентификатор события или группы.
        event_or_group (str): Событие ``event`` или группа ``group``.
        reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.

    Returns:
        dict: Кэш параметров события или группы.
    """
    event_cache_key = '{type}.{event_uuid}'.format(type=event_or_group, event_uuid=event_uuid)
    event_cache_value = cache.get(event_cache_key)
    # debug_console('event_or_group cache:', event_cache_key)

    if reset:
        cache.delete(event_cache_key)

    if not event_cache_value or reset:
        # debug_console('    getting item from DB...')
        try:
            event = dict(Event.objects.select_related(
                'event_venue',
                'domain'
            ).annotate(
                # Параметры события
                event_uuid=F('id'),
                event_title=F('title'),
                event_slug=F('slug'),
                event_datetime=F('datetime'),
                event_description=F('description'),
                event_keywords=F('keywords'),
                event_text=F('text'),
                event_min_price=F('min_price'),
                event_min_age=F('min_age'),
                event_category_slug=F('event_category__slug'),
                event_category_title=F('event_category__title'),
                event_venue_title=F('event_venue__title'),
                event_venue_city=F('event_venue__city__title'),
                is_in_group=F('event_groups'),
                # Параметры группы, если событие в неё входит
                group_uuid=F('event_groups'),

                payment_service_id=F('ticket_service__payment_service__id'),

                domain_slug=F('domain__slug'),

                city_timezone=F('domain__city__timezone'),
            ).values(
                'is_published',
                'is_on_index',
                'is_group',
                'is_in_group',

                'event_uuid',
                'event_title',
                'event_slug',
                'event_datetime',
                'event_description',
                'event_keywords',
                'event_text',
                'event_min_price',
                'event_min_age',
                'event_category_slug',
                'event_category_title',
                'event_venue_title',
                'event_venue_city',

                'group_uuid',

                'ticket_service_id',
                'ticket_service_event',
                'ticket_service_scheme',
                'ticket_service_prices',

                'payment_service_id',

                'domain_id',
                'domain_slug',

                'city_timezone'
            ).get(
                event_uuid=event_uuid,
            ))
        except Event.DoesNotExist:
            # debug_console('    nothing found!')
            return None
        else:
            # debug_console('    pre-saving...')
            # Человекопонятные локализованные дата и время события
            event_datetime_localized = event['event_datetime'].astimezone(event['city_timezone'])
            event['event_date'] = humanize_date(event_datetime_localized)
            event['event_time'] = event_datetime_localized.strftime('%H:%M')

            # Полный URL страницы события
            url = reverse(
                'event:event',
                args=[
                    event_datetime_localized.strftime('%Y'),
                    event_datetime_localized.strftime('%m'),
                    event_datetime_localized.strftime('%d'),
                    event_datetime_localized.strftime('%H'),
                    event_datetime_localized.strftime('%M'),
                    event['event_slug']
                ]
            )
            event['url'] = build_absolute_url(event['domain_slug'], url)

            # Содержится ли событие в группе - приведение к bool для удобства
            event['is_in_group'] = True if event['is_in_group'] is not None else False

            # Приведение часового пояса города к str перед кэшированием во избежание исключения
            event['city_timezone'] = str(event['city_timezone'])

            event_cache_value = {k: v for k, v in event.items()}
            cache.set(event_cache_key, json.dumps(event_cache_value, ensure_ascii=False, default=json_serializer))

            # Получение параметров события, если кэш явно НЕ инвалидировался
            # if not reset:
            #     get_or_set_cache(event_uuid, event_or_group)
    else:
        # debug_console('    pre-reading...')
        event_cache_value = json.loads(event_cache_value)
        # debug_console('    ', event_cache_value['event_title'])

        # Получение из строки даты и времени в UTC ('2017-08-31T16:00:00+00:00')
        # В шаблоне она должна локализоваться с учётом текущего часового пояса
        event_cache_value['event_datetime'] = parse(event_cache_value['event_datetime'])

        # Замена некоторых параметров события на параметры родительской группы, если событие в неё входит
        if event_cache_value['is_in_group']:
            # debug_console('    group params overriding...')

            # Получение параметров группы
            group_cache_value = get_or_set_cache(event_cache_value['group_uuid'], 'group')

            # Параметры события для замены
            group_substitutes = (
                'event_title',
                'event_min_age',
                'event_description',
                'event_text',
                'event_category_slug',
                'event_category_title',
            )

            for sub in group_substitutes:
                event_cache_value[sub] = group_cache_value[sub]
                # debug_console('    ----- ', sub)

        # Получение пути к афише в позиции `small_vertical` либо заглушки по умолчанию
        # Для событий, принадлежащих одной группе, афиша берётся из группы
        if (event_cache_value['is_group'] or event_cache_value['is_in_group']):
            item_type = 'group'
            item_uuid = event_cache_value['group_uuid']
        else:
            item_type = 'event'
            item_uuid = event_cache_value['event_uuid']

        poster_path = os.path.join(
            event_cache_value['domain_slug'],
            item_type,
            str(item_uuid)
        )

        # ВРЕМЕННО до перехода на сохранение афиш по UUID
        city_timezone = pytz.timezone(event_cache_value['city_timezone'])
        event_datetime_localized = event_cache_value['event_datetime'].astimezone(city_timezone)
        poster_path_old = os.path.join(
            event_cache_value['domain_slug'],
            item_type,
            '{date}_{time}_{slug}'.format(
                date=event_datetime_localized.strftime('%Y-%m-%d'),
                time=event_datetime_localized.strftime('%H-%M'),
                slug=event_cache_value['event_slug']
            )
        )
        # ВРЕМЕННО до перехода на сохранение афиш по UUID

        poster_file_extensions = ('png', 'jpg', 'jpeg', 'gif',)

        for ext in poster_file_extensions:
            # debug_console('    try', ext)
            poster_file = 'small_vertical.{ext}'.format(ext=ext)
            if os.path.isfile(os.path.join(settings.MEDIA_ROOT, poster_path, poster_file)):
                event_cache_value['poster'] = '{poster_path}/{poster_file}'.format(
                    poster_path=poster_path,
                    poster_file=poster_file
                )
                # debug_console('    found poster', event_cache_value['poster'])
                break
            # ВРЕМЕННО до перехода на сохранение афиш по UUID
            elif os.path.isfile(os.path.join(settings.MEDIA_ROOT, poster_path_old, poster_file)):
                event_cache_value['poster'] = '{poster_path}/{poster_file}'.format(
                    poster_path=poster_path_old,
                    poster_file=poster_file
                )
                # debug_console('    found poster', event_cache_value['poster'])
                break
            # ВРЕМЕННО до перехода на сохранение афиш по UUID
        else:
            event_cache_value['poster'] = 'global/event/small_vertical.png'.format(
                media_url=settings.MEDIA_URL
            )

        # debug_console('    reading...')

        return event_cache_value
