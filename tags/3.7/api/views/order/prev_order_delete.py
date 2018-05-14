import uuid

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket

from api.shortcuts import JsonResponseUTF8


def prev_order_delete(request):
    """Попытка удалить старый предварительный резерв из другого события, если он был сделан ранее."""
    if request.is_ajax() and request.method == 'POST':
        # UUID события
        event_uuid = request.POST.get('event_uuid', None)
        try:
            event_uuid = uuid.UUID(event_uuid)
        except (TypeError, ValueError):
            response = {'success': False, 'message': 'UUID события некорректен или отсутствует'}
            return JsonResponseUTF8(response)

        # UUID предварительного резерва
        order_uuid = request.POST.get('order_uuid', None)
        if order_uuid:
            try:
                order_uuid = uuid.UUID(order_uuid)
            except (TypeError, ValueError):
                response = {'success': False, 'message': 'UUID предварительного резерва некорректен или отсутствует'}
                return JsonResponseUTF8(response)

        # Получение предварительного резерва в предыдущем событии
        prev_basket = OrderBasket(order_uuid=order_uuid, logger='bezantrakta.prev_order_delete')
        if not prev_basket or not prev_basket.order:
            response = {'success': False, 'message': 'Отсутствует предварительный резерв с указанным UUID'}
            return JsonResponseUTF8(response)

        # Информация из предыдущего события
        prev_event_id = prev_basket.order['event_id']

        # Информация из текущего события
        this_event = cache_factory('event', event_uuid)
        this_event_id = this_event['ticket_service_event']

        response = {}

        if prev_event_id != this_event_id:
            prev_basket.logger.info('\n----------Удаление предварительного резерва в другом событии----------')
            prev_basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

            prev_basket.logger.info('prev_event_id: {}'.format(prev_event_id))
            prev_basket.logger.info('this_event_id: {}'.format(this_event_id))

            # Освобождение билетов и удаление предварительного резерва
            response = prev_basket.tickets_clear()
        else:
            response['success'] = False
            response['message'] = 'Удаление предварительного резерва НЕ требуется'
            response['tickets'] = {}

        return JsonResponseUTF8(response)
