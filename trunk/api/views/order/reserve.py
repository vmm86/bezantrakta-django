import logging

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket

from api.shortcuts import JsonResponseUTF8


def reserve(request):
    """Добавление или удаление места в предварительном резерве мест."""
    if request.is_ajax() and request.method == 'POST':
        logger = logging.getLogger('bezantrakta.reserve')

        # UUID события
        event_uuid = request.POST.get('event_uuid', None)
        if not event_uuid:
            response = {'success': False, 'message': 'Отсутствует UUID события'}
            return JsonResponseUTF8(response)

        # UUID заказа
        order_uuid = request.POST.get('order_uuid', None)
        if not order_uuid:
            response = {'success': False, 'message': 'Отсутствует UUID предварительного резерва'}
            return JsonResponseUTF8(response)

        # Идентификатор билета
        ticket_id = request.POST.get('ticket_id', None)
        if not ticket_id:
            response = {'success': False, 'message': 'Отсутствует идентификатор билета для резерва'}
            return JsonResponseUTF8(response)

        action = request.POST.get('action', 'add')

        # Получение параметров сайта
        domain = cache_factory('domain', request.domain_slug)

        # Информация о событии из кэша
        event = cache_factory('event', event_uuid)
        if not event:
            response = {'success': False, 'message': 'Отсутствует запрошенное событие'}
            return JsonResponseUTF8(response)

        # Информация о сервисе продажи билетов из кэша
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])

        # Получение существующего ранее инициализированного предварительного резерва
        basket = OrderBasket(order_uuid=order_uuid)

        logger.info('\n----------reserve----------')
        logger.info('{:%Y-%m-%d %H:%M:%S}'.format(timezone_now()))

        logger.info('Сайт: {}'.format(domain['domain_title']))
        logger.info('Сервис продажи билетов: {title} ({id})'.format(
                title=ticket_service['title'],
                id=ticket_service['id']
            )
        )

        logger.info('Название события: "{}"'.format(event['event_title']))
        logger.info('UUID события: "{}"'.format(event_uuid))
        logger.info('Идентификатор события: {}'.format(event['ticket_service_event']))

        logger.info('UUID заказа: "{}"'.format(order_uuid))
        if action == 'add':
            logger.info('\nДействие: добавить')
        elif action == 'remove':
            logger.info('\nДействие: удалить')

        logger.info('\nПредыдущее состояние заказа:')
        if basket.order['tickets']:
            logger.info('    Билеты в заказе:')
            for t in basket.order['tickets']:
                logger.info('    * {}'.format(t))
        else:
            logger.info('    Билеты в заказе: []')
        logger.info('    Число билетов: {}'.format(basket.order['tickets_count']))
        logger.info('    Сумма цен на билеты: {}'.format(basket.order['total']))

        # Добавление или удаление билета в предварительном резерве
        response = basket.toggle_ticket(ticket_id, action)

        if (action == 'add' and response['success']) or action == 'remove':
            logger.info('\nИдентификатор билета: {}'.format(ticket_id))

            logger.info('\nПоследующее состояние заказа:')
            if basket.order['tickets']:
                logger.info('    Билеты в заказе:')
                for t in basket.order['tickets']:
                    logger.info('    * {}'.format(t))
            else:
                logger.info('    Билеты в заказе: []')
            logger.info('    Число билетов: {}'.format(basket.order['tickets_count']))
            logger.info('    Сумма цен на билеты: {}'.format(basket.order['total']))

        return JsonResponseUTF8(response)
