import logging
import uuid
from time import sleep

from django.http import JsonResponse

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket


def prev_order_delete(request):
    """Попытка удалить предыдущий предварительный резерв из другого события (если он был создан ранее)."""

    # Класс для работы с заказом (на данный момент - с предварительным резервом)
    # Получение предыдущего заказа, который в новом событии необходимо очистить
    if request.is_ajax() and request.method == 'POST':
        logger = logging.getLogger('bezantrakta.reserve')

        # Идентификатор события
        event_id = request.POST.get('event_id', None)
        # UUID заказа
        order_uuid = request.POST.get('order_uuid', None)
        # Если идентификатор события или UUID заказа не получен - возвращается НЕуспешный ответ с ошибкой
        if not event_id:
            response = {'success': False, 'message': 'Отсутствует идентификатор события'}
            return JsonResponse(response, safe=False)
        if not order_uuid:
            response = {'success': False, 'message': 'Отсутствует UUID заказа'}
            return JsonResponse(response, safe=False)

        # Получение параметров сайта
        domain = cache_factory('domain', request.domain_slug)

        basket = OrderBasket(order_uuid=order_uuid)

        logger.info('\n------------------------------------------------------------')
        logger.info('event_id: {}'.format(event_id))
        logger.info('order_uuid: {}'.format(order_uuid))
        logger.info('basket.order[tickets]: {}'.format(basket.order['tickets']))

        # Если предварительный резерв не существует - возвращается НЕуспешный ответ с ошибкой
        if not basket or not basket.order:
            response = {'success': False, 'message': 'Отсутствует предварительный резерв с указанным UUID'}
            return JsonResponse(response, safe=False)
        else:
            if not basket.order['tickets']:
                # Удалить кэш старого предварительного резерва
                # basket.delete_order_cache()
                response = {'success': False, 'message': 'В предварительном резерве нет билетов'}
                return JsonResponse(response, safe=False)

        # Информация о сервисе продажи билетов из кэша
        ticket_service = cache_factory('ticket_service', basket.order['ticket_service_id'])
        ts = ticket_service['instance']

        now = timezone_now()
        logger.info('\n----------Отмена предыдущего предварительного резерва {}----------'.format(order_uuid))
        logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

        logger.info('Сайт: {title} ({id})'.format(title=domain['domain_title'], id=domain['domain_id']))
        logger.info('Сервис продажи билетов: {title} ({id})'.format(
                title=ticket_service['title'],
                id=ticket_service['id']
            )
        )

        logger.info('Билетов в заказе: {}'.format(len(basket.order['tickets'])))

        # Формирование ответа
        response = {}
        response['tickets'] = []

        logger.info('\nОтмена предварительного резерва билетов...')
        # Отмена предварительного резерва для каждого из билетов
        for ticket in basket.order['tickets']:
            logger.info('\n    * {}'.format(ticket))

            # Параметры для отправки запроса к сервису продажи билетов
            params = {}
            params['event_id'] = event_id
            params['order_uuid'] = order_uuid
            params['action'] = 'remove'

            keys = (
                'sector_id',
                'sector_title',
                'row_id',
                'seat_id',
                'seat_title',
                'price_group_id',
                'price',
                'price_order',
            )

            for k in keys:
                params[k] = ticket[k] if k in ticket else None

            # logger.info('    params: {}'.format(params))

            # Удаление места из предварительного резерва
            remove = ts.reserve(**params)
            # logger.info('    remove: {}'.format(remove))

            response['success'] = True if remove['success'] else False

            if remove['success']:
                response['tickets'].append(params)
                logger.info('    Резерв билета успешно отменён')
            else:
                logger.info('    НЕ удалось отменить резерв билета')

            # basket.remove_ticket(params)

            # Задержка в 2 секунды во избежание возможных ошибок
            sleep(2)

        # Удалить кэш старого предварительного резерва
        basket.delete_order_cache()

        return JsonResponse(response, safe=False)
