import logging
import uuid
from random import randint
from time import sleep

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order import OrderBasket

from api.shortcuts import JsonResponseUTF8


def prev_order_delete(request):
    """Попытка удалить старый предварительный резерв из другого события, если он был сделан ранее.

    Единичный заказ действует только в рамках одного события.
    Если идентификаторы предыдущего и текущего событий не совпадают, старый предварительный резерв удаляется.
    """
    #
    if request.is_ajax() and request.method == 'POST':
        logger = logging.getLogger('bezantrakta.reserve')

        # UUID события
        event_uuid = request.POST.get('event_uuid', None)
        try:
            event_uuid = uuid.UUID(event_uuid)
        except (TypeError, ValueError):
            response = {'success': False, 'message': 'UUID события некорректен или отсутствует'}
            return JsonResponseUTF8(response, status=400)

        # UUID предварительного резерва
        order_uuid = request.POST.get('order_uuid', None)
        if order_uuid:
            try:
                order_uuid = uuid.UUID(order_uuid)
            except (TypeError, ValueError):
                response = {'success': False, 'message': 'UUID предварительного резерва некорректен или отсутствует'}
                return JsonResponseUTF8(response, status=400)

        # Получение параметров сайта
        domain = cache_factory('domain', request.domain_slug)

        logger.info('\n----------prev_order_remove----------'.format(order_uuid))
        logger.info('{:%Y-%m-%d %H:%M:%S}'.format(timezone_now()))
        logger.info('Сайт: {title} ({id})'.format(title=domain['domain_title'], id=domain['domain_id']))

        # Получение предварительного резерва в предыдущем событии
        basket = OrderBasket(order_uuid=order_uuid)

        if not basket or not basket.order:
            response = {'success': False, 'message': 'Отсутствует предварительный резерв с указанным UUID'}
            return JsonResponseUTF8(response, status=404)

        if not basket.order['tickets']:
            # Удаление старого предварительного резерва (без билетов)
            basket.delete_order()
            response = {
                'success': True,
                'tickets': None,
                'message': 'Старый предварительный резерв (без билетов) успешно удалён'
            }
            return JsonResponseUTF8(response)

        logger.info('order_uuid: {} {}'.format(order_uuid, str(type(order_uuid))))
        logger.info('\nПредыдущий предварительный резерв: {}'.format(basket.order))

        # Информация из предыдущего события
        prev_ticket_service_id = basket.order['ticket_service_id']
        prev_event_id = basket.order['event_id']

        # Информация из текущего события
        this_event = cache_factory('event', basket.order['event_uuid'])
        this_event_id = this_event['ticket_service_event']

        logger.info('prev_ticket_service_id: {} {}'.format(prev_ticket_service_id, str(type(prev_ticket_service_id))))
        logger.info('prev_event_id: {} {}'.format(prev_event_id, str(type(prev_event_id))))
        logger.info('this_event_id: {} {}'.format(this_event_id, str(type(this_event_id))))

        # Формирование ответа
        response = {}

        if prev_event_id != this_event_id:
            response['success'] = True
            response['tickets'] = {}

            logger.info('\nОтмена предыдущего предварительного резерва...')

            # Информация о сервисе продажи билетов в предыдущем событии
            prev_ticket_service = cache_factory('ticket_service', prev_ticket_service_id)
            prev_ts = prev_ticket_service['instance']

            # Отмена предварительного резерва для каждого из билетов
            for ticket_id in basket.order['tickets']:
                logger.info('\n    * {}'.format(basket.order['tickets'][ticket_id]))

                # Параметры для отправки запроса к сервису продажи билетов
                params = {
                    'event_id':   prev_event_id,
                    'order_uuid': order_uuid,
                    'ticket_id':  ticket_id,
                    'action':     'remove',
                }

                # Удаление места из предварительного резерва
                remove = prev_ts.reserve(**params)
                response['tickets'][ticket_id] = basket.order['tickets'][ticket_id]

                logger.info('    remove: {}'.format(remove))

                if remove['success']:
                    response['tickets'][ticket_id]['removed'] = True
                    logger.info('    Билет успешно удалён из предварительного резерва')
                else:
                    response['tickets'][ticket_id]['removed'] = False
                    logger.info('    Билет НЕ удалось удалить из предварительного резерва')

                # Задержка в несколько секунд во избежание возможных ошибок
                sleep(randint(2, 5))

            # Удаление старого предварительного резерва
            basket.delete_order()
            response['message'] = 'Старый предварительный резерв успешно удалён'
        else:
            response['success'] = False
            response['message'] = 'Удаление предварительного резерва НЕ требуется'

        return JsonResponseUTF8(response)
