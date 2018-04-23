import logging
import urllib
import uuid

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket
from bezantrakta.order.shortcuts import new_blank_order

from api.shortcuts import JsonResponseUTF8


def initialize(request):
    """Инициализация существующего предварительного резерва (ПР) на 1 или 2 шагах заказа билетов.

    Если ПР по каким-то причинам НЕ существует - будет создан новый пустой ПР.
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

        logger.info('\n----------Инициализация предварительного резерва----------')
        logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

        # Информация о текущем событии
        this_event = cache_factory('event', event_uuid)
        if not this_event:
            response = {'success': False, 'message': 'Отсуствует информация о событии'}
            return JsonResponseUTF8(response)
        this_event_id = this_event['ticket_service_event']

        # Получение реквизитов покупателя из cookies
        customer = {
            'name':       request.COOKIES.get('bezantrakta_customer_name',       None),
            'phone':      request.COOKIES.get('bezantrakta_customer_phone',      None),
            'email':      request.COOKIES.get('bezantrakta_customer_email',      None),
            'address':    request.COOKIES.get('bezantrakta_customer_address',    None),
            'order_type': request.COOKIES.get('bezantrakta_customer_order_type', None)
        }
        customer = {k: urllib.parse.unquote(v) for k, v in customer.items() if v}

        log_order = {}
        # Если order_uuid получен - пытаемся получить существующий предварительный резерв
        if order_uuid:
            # Получение существующего предварительного резерва
            basket = OrderBasket(order_uuid=order_uuid)

            log_order['uuid'] = None
            log_order['state'] = None
            # Если предварительный резерв с полученным order_uuid по каким-то причинам НЕ существует
            if not basket or not basket.order:
                # Создаётся новый пустой предварительный резерв
                logger.info('\nПредварительный резерв {} НЕ существует'.format(order_uuid))

                basket = new_blank_order(event_uuid, customer=customer)
                log_order['uuid'] = basket.order['order_uuid']
                log_order['state'] = 'Новый пустой предварительный резерв'
            else:
                now = basket.now()
                updated = basket.order.get('updated', basket.now())
                order_timeout_delta = (now - updated).seconds // 60 % 60
                seat_timeout = basket.ticket_service['seat_timeout']
                order_status = basket.order['status']

                if order_status not in ('reserved',):
                    logger.info('\nЗаказ {} уже создан и НЕ является предварительным резервом\n'.format(order_uuid))
                    logger.info('order_status: {}'.format(order_status))

                    basket.delete()

                    basket = new_blank_order(event_uuid, customer=customer)
                    log_order['uuid'] = basket.order['order_uuid']
                    log_order['state'] = 'Новый пустой предварительный резерв'
                # Если со времени последнего обновления заказа прошло больше минут,
                # чем таймаут на автоматическое освобождение мест (по умолчанию - 15 минут)
                elif order_timeout_delta > seat_timeout:
                    # Создаётся новый пустой предварительный резерв
                    logger.info('\nСтарый предварительный резерв {} истёк\n'.format(order_uuid))

                    logger.info('\nnow: {}'.format(now))
                    logger.info('updated: {}'.format(updated))
                    logger.info('delta: {}'.format(order_timeout_delta))
                    logger.info('seat_timeout: {}'.format(seat_timeout))

                    basket.delete()
                    basket = new_blank_order(event_uuid, customer=customer)
                    log_order['uuid'] = basket.order['order_uuid']
                    log_order['state'] = 'Новый пустой предварительный резерв'
                else:
                    log_order['uuid'] = order_uuid
                    log_order['state'] = 'Существующий предварительный резерв'

                    # Информация о предыдущем событии
                    prev_event_id = basket.order['event_id']
                    prev_ticket_service_id = basket.ticket_service['id']

                    # Если существующий предварительный резерв был сделан в другом событии
                    if prev_event_id != this_event_id:
                        logger.info('prev_ticket_service_id: {}'.format(prev_ticket_service_id))
                        logger.info('prev_event_id: {}'.format(prev_event_id))
                        logger.info('this_event_id: {}'.format(this_event_id))

                        # Этот предварительный резерв будет удалён при параллельном запуске ``prev_order_delete``
                        # Создаётся новый пустой предварительный резерв
                        basket = new_blank_order(event_uuid, customer=customer)
                        log_order['uuid'] = basket.order['order_uuid']
                        log_order['state'] = 'Новый пустой предварительный резерв'
        # Если order_uuid НЕ получен
        else:
            # Создаётся новый пустой предварительный резерв
            basket = new_blank_order(event_uuid, customer=customer)
            log_order['uuid'] = basket.order['order_uuid']
            log_order['state'] = 'Новый пустой предварительный резерв'

        logger.info('\nUUID предварительного резерва: {}'.format(log_order['uuid']))
        logger.info('{}: {}'.format(log_order['state'], basket.order))

        # Формирование ответа
        response = {}
        response['success'] = True
        response['order'] = basket.order
        response['heartbeat_timeout'] = basket.ticket_service['heartbeat_timeout']
        response['seat_timeout'] = basket.ticket_service['seat_timeout']

        return JsonResponseUTF8(response)
