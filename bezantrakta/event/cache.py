from dateutil.parser import parse
import simplejson as json

from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.urls.base import reverse

from project.shortcuts import build_absolute_url, json_serializer, humanize_date

from .models import Event


def get_or_set_cache(event_uuid, reset=False):
    """Кэширование параметров события для последующего использования без запросов в БД.

    Args:
        event_uuid (UUID): Уникальный идентификатор события.
        reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.

    Returns:
        dict: Кэш параметров события.
    """
    cache_key = 'event.{event_uuid}'.format(event_uuid=event_uuid)
    cache_value = cache.get(cache_key)

    if reset:
        cache.delete(cache_key)

    if not cache_value or reset:
        try:
            event = dict(Event.objects.select_related(
                'event_venue',
                'domain'
            ).annotate(
                # Содержится ли событие в группе
                is_in_group=F('event_groups'),
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
                event_venue_title=F('event_venue__title'),
                event_venue_city=F('event_venue__city__title'),
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
            return None
        else:
            # Человекопонятные локализованные дата и время события
            event_datetime_localized = event['event_datetime'].astimezone(event['city_timezone'])
            event['event_date'] = humanize_date(event_datetime_localized)
            event['event_time'] = event_datetime_localized.strftime('%H:%M')

            # Приведение часового пояса города к str во избежание исключения
            event['city_timezone'] = str(event['city_timezone'])

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

            cache_value = {k: v for k, v in event.items()}
            cache.set(cache_key, json.dumps(cache_value, ensure_ascii=False, default=json_serializer))
    else:
        cache_value = json.loads(cache.get(cache_key))
        # Получение из строки даты и времени в UTC ('2017-08-31T16:00:00+00:00')
        # В шаблоне она должна локализоваться с учётом текущего часового пояса
        cache_value['event_datetime'] = parse(cache_value['event_datetime'])

    return cache_value
