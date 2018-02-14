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

        # Получение существующего ранее инициализированного предварительного резерва
        basket = OrderBasket(order_uuid=order_uuid)

        # Информация о событии из кэша
        event = cache_factory('event', event_uuid)
        event_id = event['ticket_service_event']

        if not event:
            response = {'success': False, 'message': 'Отсутствует запрошенное событие'}
            return JsonResponseUTF8(response)

        # Информация о сервисе продажи билетов из кэша
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        ts = ticket_service['instance']

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

        logger.info('\nИдентификатор билета: {}'.format(ticket_id))

        logger.info('\nПредыдущее состояние заказа:')
        if basket.order['tickets']:
            logger.info('    Билеты в заказе:')
            for t in basket.order['tickets']:
                logger.info('    * {}'.format(t))
        else:
            logger.info('    Билеты в заказе: []')
        logger.info('    Число билетов: {}'.format(basket.order['tickets_count']))
        logger.info('    Сумма цен на билеты: {}'.format(basket.order['total']))

        # Параметры для отправки запроса к сервису продажи билетов
        params = {}
        params['event_id'] = event_id
        params['order_uuid'] = order_uuid
        params['ticket_id'] = ticket_id
        params['action'] = action

        # Текущее состояние мест и цен в событии
        seats_and_prices = cache_factory('seats_and_prices', event_uuid)

        # Универсальный метод для работы с предварительным резервом мест
        reserve = ts.reserve(**params)
        logger.info('\nreserve: {}'.format(reserve))

        if reserve['success']:
            if action == 'add':
                ticket = seats_and_prices['seats'][ticket_id]
                logger.info('\nticket: {}'.format(ticket))
                basket.add_ticket(ticket_id, ticket)
            elif action == 'remove':
                basket.remove_ticket(ticket_id)

            response = reserve

            response['tickets_count'] = basket.order['tickets_count']
            response['tickets'] = basket.order['tickets']
            response['total'] = basket.order['total']

            logger.info('\nresponse: {}'.format(response))

            logger.info('\nПоследующее состояние заказа:')
            if basket.order['tickets']:
                logger.info('    Билеты в заказе:')
                for t in basket.order['tickets']:
                    logger.info('    * {}'.format(t))
            else:
                logger.info('    Билеты в заказе: []')
            logger.info('    Число билетов: {}'.format(basket.order['tickets_count']))
            logger.info('    Сумма цен на билеты: {}'.format(basket.order['total']))
        else:
            if action == 'add':
                logger.info('Код ошибки: {}'.format(reserve['code']))
                logger.info('Сообщение об ошибке: {}'.format(reserve['message']))
                response = {'success': False, 'code': reserve['code'], 'message': reserve['message']}
                return JsonResponseUTF8(response)
            # Даже если при удалении билета получен НЕуспешный ответ -
            # билет в любом случае удаляется из предварительного резерва
            elif action == 'remove':
                basket.remove_ticket(ticket_id)

        return JsonResponseUTF8(response)
