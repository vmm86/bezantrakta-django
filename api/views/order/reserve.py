import logging
import uuid
import simplejson as json

from django.http import JsonResponse

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket


def reserve(request):
    """Добавление или удаление места в предварительном резерве мест."""
    if request.is_ajax() and request.method == 'POST':
        logger = logging.getLogger('bezantrakta.reserve')

        # UUID события
        event_uuid = request.POST.get('event_uuid', None)
        # UUID заказа
        order_uuid = request.POST.get('order_uuid', uuid.uuid4())

        seat = json.loads(request.POST.get('seat', {}))
        action = request.POST.get('action', 'add')

        # Если UUID события или места не получен - возвращается НЕуспешный ответ с ошибкой
        if not event_uuid:
            return {'success': False, 'message': 'Отсутствует уникальный идентификатор события'}
        if not seat:
            return {'success': False, 'message': 'Отсутствует место для резерва'}

        # Получение параметров сайта
        domain = cache_factory('domain', request.domain_slug)

        # Информация о событии из кэша
        event = cache_factory('event', event_uuid)

        # Информация о сервисе продажи билетов из кэша
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        ts = ticket_service['instance']

        # Класс для работы с заказом (на данный момент - с предварительным резервом)
        # Создание нового пустого заказа в файловом кэше или получение имеющегося
        basket = OrderBasket(
            order_uuid=order_uuid,
            ticket_service_id=ticket_service['id'],
            event_uuid=event_uuid,
            event_id=event['ticket_service_event'],
        )

        now = timezone_now()
        logger.info('\n----------Предварительный резерв {}----------'.format(order_uuid))
        logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

        logger.info('Сайт: {title} ({id})'.format(title=domain['domain_title'], id=domain['domain_id']))
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

        logger.info('\nВыбранное место: {}'.format(seat))

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
        params['event_id'] = event['ticket_service_event']
        params['order_uuid'] = order_uuid
        params['action'] = action

        keys = (
            ('sector_id', int,),
            ('sector_title', str,),
            ('row_id', int,),
            ('seat_id', int,),
            ('seat_title', str,),
            ('price_group_id', int,),
            ('price', str,),
            ('price_order', int,),
        )
        # Преобразование типов
        for k in keys:
            try:
                params[k[0]] = k[1](seat[k[0]]) if k[0] in seat else None
            except (TypeError, ValueError):
                params[k[0]] = None

        # Формирование ответа
        response = {k[0]: params[k[0]] for k in keys}
        response['action'] = action

        # Универсальный метод для работы с предварительным резервом мест
        reserve = ts.reserve(**params)

        response['success'] = True if reserve['success'] else False

        if not reserve['success']:
            response['code'] = reserve['code']
            response['message'] = reserve['message']
            return JsonResponse(response, safe=False)

        # logger.info('response: {}'.format(response))

        if action == 'add':
            basket.add_ticket(response)
        elif action == 'remove':
            basket.remove_ticket(response)

        logger.info('\nПоследующее состояние заказа:')
        if basket.order['tickets']:
            logger.info('    Билеты в заказе:')
            for t in basket.order['tickets']:
                logger.info('    * {}'.format(t))
        else:
            logger.info('    Билеты в заказе: []')
        logger.info('    Число билетов: {}'.format(basket.order['tickets_count']))
        logger.info('    Сумма цен на билеты: {}'.format(basket.order['total']))

        return JsonResponse(response, safe=False)
