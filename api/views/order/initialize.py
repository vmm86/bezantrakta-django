import logging
import uuid

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket
from bezantrakta.order.shortcuts import new_blank_order

from api.shortcuts import JsonResponseUTF8


def initialize(request):
    """Получение информации о предварительном резерве на 1 или 2 шагах заказа билетов.

    Если предварительный резерв по каким-то причинам НЕ существует - будет создан новый пустой предварительный резерв.
    """
    if request.is_ajax() and request.method == 'GET':
        logger = logging.getLogger('bezantrakta.reserve')

        # UUID события
        event_uuid = request.GET.get('event_uuid', None)
        try:
            event_uuid = uuid.UUID(event_uuid)
        except (TypeError, ValueError):
            response = {'success': False, 'message': 'UUID события некорректен или отсутствует'}
            return JsonResponseUTF8(response)

        # UUID предварительного резерва
        order_uuid = request.GET.get('order_uuid', None)
        if order_uuid:
            try:
                order_uuid = uuid.UUID(order_uuid)
            except (TypeError, ValueError):
                order_uuid = None

        # Получение параметров сайта
        domain = cache_factory('domain', request.domain_slug)

        logger.info('\n----------order_initialize----------'.format(order_uuid))
        logger.info('{:%Y-%m-%d %H:%M:%S}'.format(timezone_now()))
        logger.info('Сайт: {title} ({id})'.format(title=domain['domain_title'], id=domain['domain_id']))

        # Если order_uuid получен - пытаемся получить существующий предварительный резерв
        if order_uuid:
            # Получение существующего предварительного резерва
            basket = OrderBasket(order_uuid=order_uuid)

            log_order = {'uuid': None, 'state': None, }
            # Если предварительный резерв с полученным order_uuid по каким-то причинам НЕ существует
            if not basket or not basket.order:
                # Создаётся новый пустой предварительный резерв
                basket = new_blank_order(event_uuid)
                logger.info('\nПредварительный резерв {} НЕ существует'.format(order_uuid))
                log_order['uuid'] = basket.order['order_uuid']
                log_order['state'] = 'Новый пустой предварительный резерв'
            else:
                log_order['uuid'] = order_uuid
                log_order['state'] = 'Существующий предварительный резерв'

            # Информация из предыдущего события
            prev_ticket_service_id = basket.order['ticket_service_id']
            prev_event_id = basket.order['event_id']

            # Информация из текущего события
            this_event = cache_factory('event', basket.order['event_uuid'])
            this_event_id = this_event['ticket_service_event']

            logger.info('prev_ticket_service_id: {} {}'.format(prev_ticket_service_id))
            logger.info('prev_event_id: {} {}'.format(prev_event_id))
            logger.info('this_event_id: {} {}'.format(this_event_id))

            # Если существующий предварительный резерв был сделан в другом событии
            if prev_event_id != this_event_id:
                # Этот предварительный резерв будет удалён при параллельном запуске ``prev_order_delete``
                # Создаётся новый пустой предварительный резерв
                basket = new_blank_order(event_uuid)
                log_order['uuid'] = basket.order['order_uuid']
                log_order['state'] = 'Новый пустой предварительный резерв'
        # Если order_uuid НЕ получен
        else:
            # Создаётся новый пустой предварительный резерв
            basket = new_blank_order(event_uuid)
            log_order['uuid'] = basket.order['order_uuid']
            log_order['state'] = 'Новый пустой предварительный резерв'

        logger.info('order_uuid: {}'.format(log_order['uuid']))
        logger.info('{}: {}'.format(log_order['state'], basket.order))

        # Формирование ответа
        response = {}
        response['success'] = True
        response['order'] = basket.order

        return JsonResponseUTF8(response)
