import simplejson as json

from django.core.cache import cache


def get_or_set_cache(order_uuid, ticket_service_id):
    # Формирование заказа в кэше на стороне сервера
    order_cache_key = 'order_{order_uuid}'.format(order_uuid=order_uuid)
    order_cache_value = cache.get(order_cache_key)

    if not order_cache_value:
        order_cache_value = {}
        order_cache_value['ticket_service_id'] = ticket_service_id
        order_cache_value['order_uuid'] = order_uuid

        order_cache_value['order_tickets'] = []
        order_cache_value['order_count'] = 0
        order_cache_value['order_total'] = 0
    else:
        pass

    order_cache_value = json.dumps(order_cache_value, ensure_ascii=False)
    cache.set(order_cache_key, order_cache_value)

    print('\norder ', order_cache_key, ':\n', order_cache_value, '\n')
