import simplejson as json

from django.core.cache import cache

from project.shortcuts import build_absolute_url, debug_console, json_serializer, humanize_date


def reserve_cache(order_uuid, ticket_service_id, reset=False):
    """Кэширование информации о предварительном резерве, ещё не подтверждённом в заказ.

    Args:
        order_uuid (UUID): Уникальный идентификатор рзерва и будущего заказа.
        ticket_service_id (str): Идентификатор сервиса продажи билетов.
        reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.
    """
    cache_key = 'reserve.{order_uuid}'.format(order_uuid=order_uuid)
    cache_value = cache.get(cache_key)
    debug_console('event_or_group cache:', cache_key)

    if reset:
        cache.delete(cache_key)

    if not cache_value or reset:
        cache_value = {}
        cache_value['ticket_service_id'] = ticket_service_id
        cache_value['order_uuid'] = order_uuid

        cache_value['order_tickets'] = []
        cache_value['order_count'] = 0
        cache_value['order_total'] = 0
    else:
        pass

    cache_value = json.dumps(cache_value, ensure_ascii=False)
    cache.set(cache_key, cache_value)

    # print('\norder ', cache_key, ':\n', cache_value, '\n')
