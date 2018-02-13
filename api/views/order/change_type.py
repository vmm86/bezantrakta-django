import logging

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order import OrderBasket
from bezantrakta.order.settings import ORDER_TYPE, ORDER_TYPE_MAPPING

from api.shortcuts import JsonResponseUTF8


def change_type(request):
    if request.is_ajax() and request.method == 'POST':
        logger = logging.getLogger('bezantrakta.reserve')

        # UUID заказа
        order_uuid = request.POST.get('order_uuid', None)
        # Выбранный тип заказа
        order_type = request.POST.get('order_type', None)

        if not order_uuid:
            response = {'success': False, 'message': 'Отсутствует UUID предварительного резерва'}
            return JsonResponseUTF8(response, status=404)

        if not order_type:
            response = {'success': False, 'message': 'Отсутствует тип заказа'}
            return JsonResponseUTF8(response, status=404)
        else:
            if order_type not in ORDER_TYPE:
                response = {'success': False, 'message': 'Указан некорректный тип заказа'}
            return JsonResponseUTF8(response, status=400)

        # Класс для работы с заказом (на данный момент - с предварительным резервом)
        basket = OrderBasket(order_uuid=order_uuid)

        # Если предварительный резерв не существует - возвращается НЕуспешный ответ с ошибкой
        if not basket or not basket.order:
            response = {'success': False, 'message': 'Отсутствует предварительный резерв с указанным UUID'}
            return JsonResponseUTF8(response, status=404)
        # else:
        #     if not basket.order['tickets']:
        #         response = {'success': False, 'message': 'В предварительном резерве нет билетов'}
        #         return JsonResponse(response, safe=False)

        # Информация о событии, UUID которого сохранён в предварительном резерве
        event = cache_factory('event', basket.order['event_uuid'])

        if not event:
            response = {'success': False, 'message': 'Отсутствует событие с указанным UUID'}
            return JsonResponseUTF8(response, status=404)

        # Информация о сервисе продажи билетов
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        # Экземпляр класса сервиса продажи билетов
        ts = ticket_service['instance']

        # Информация о сервисе онлайн-оплаты
        payment_service = cache_factory('payment_service', event['payment_service_id'])
        # Экземпляр класса сервиса онлайн-оплаты, если она присутствует
        ps = payment_service['instance'] if payment_service else None

        # Добавление или изменение необходимых параметров предварительного резерва
        basket.order['order_type'] = order_type
        basket.order['delivery'] = ORDER_TYPE_MAPPING[order_type]['delivery']
        basket.order['payment'] = ORDER_TYPE_MAPPING[order_type]['payment']

        basket.order['extra'] = event['settings']['extra'][order_type]
        # Стоимость доставки курьером, если она используется
        basket.order['courier_price'] = basket.decimal_price(ticket_service['settings']['courier_price'])
        # Процент комиссии сервиса онлайн-оплаты, если он используется
        basket.order['commission'] = basket.decimal_price(
            payment_service['settings']['init']['commission'] if payment_service else 0
        )

        # Получение общей суммы заказа и её подписи в зависимости от возможных наценок/скидок
        basket.get_overall()

        # Обновление заказа с новыми полученными данными
        basket.update_order()

        response = basket.order

        logger.info('\n------------------------------------------------------------')
        logger.info('order_uuid: {}'.format(order_uuid))
        logger.info('order_type: {}'.format(order_type))
        logger.info('order: {}'.format(basket.order))

        logger.info('response: {}'.format(response))

        return JsonResponseUTF8(response)
