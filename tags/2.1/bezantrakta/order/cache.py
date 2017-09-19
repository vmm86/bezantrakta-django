import simplejson as json

from django.core.cache import cache


def get_or_set_cache(order_uuid, ticket_service_id, reset=False):
    """Кэширование информации о заказе (**TODO** - на будущее, пока не работает).

    Args:
        order_uuid (UUID): Уникальный идентификатор заказа.
        ticket_service_id (str): Идентификатор сервиса продажи билетов.
        reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.
    """
    cache_key = 'order_{order_uuid}'.format(order_uuid=order_uuid)
    cache_value = cache.get(cache_key)

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
