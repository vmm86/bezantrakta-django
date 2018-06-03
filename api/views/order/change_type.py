import simplejson as json
import uuid

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket

from api.shortcuts import JsonResponseUTF8


def change_type(request):
    """Изменение типа заказа на шаге 2 заказа билетов."""
    if request.is_ajax() and request.method == 'POST':
        customer = request.POST.get('customer', None)
        try:
            customer = json.loads(customer)
        except (TypeError, ValueError):
            response = {'success': False, 'message': 'Реквизиты покупателя некорректны или отсутствуют'}
            return JsonResponseUTF8(response)
        else:
            if not isinstance(customer, dict):
                response = {'success': False, 'message': 'Реквизиты покупателя некорректны или отсутствуют'}
                return JsonResponseUTF8(response)

        # UUID предварительного резерва
        order_uuid = request.POST.get('order_uuid', None)
        try:
            order_uuid = uuid.UUID(order_uuid)
        except (TypeError, ValueError):
            response = {'success': False, 'message': 'UUID предварительного резерва некорректен или отсутствует'}
            return JsonResponseUTF8(response)

        # Выбранный тип заказа
        order_type = request.POST.get('order_type', None)
        if not order_type:
            response = {'success': False, 'message': 'Отсутствует тип заказа'}
            return JsonResponseUTF8(response)

        # Получение существующего предварительного резерва
        basket = OrderBasket(order_uuid=order_uuid)
        if not basket or not basket.order:
            response = {'success': False, 'message': 'Отсутствует предварительный резерв с указанным UUID'}
            return JsonResponseUTF8(response)

        if order_type not in basket.ORDER_TYPE:
            response = {'success': False, 'message': 'Получен некорректный тип заказа'}
            return JsonResponseUTF8(response)

        # Информация о событии, UUID которого сохранён в предварительном резерве
        event = cache_factory('event', basket.order['event_uuid'])
        if not event:
            response = {'success': False, 'message': 'Отсутствует событие с указанным UUID'}
            return JsonResponseUTF8(response)

        # Изменение способа заказа билетов в предварительном резерве
        basket.order_type_change(customer, order_type)

        response = {}
        response['success'] = True
        response['order'] = basket.order

        basket.logger.info('\n----------Изменение типа заказа----------')
        basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

        basket.logger.info('UUID предварительного резерва: {}'.format(basket.order['order_uuid']))

        basket.logger.info('\nПолучение билетов: {}'.format(basket.order['delivery']))
        basket.logger.info('Оплата билетов: {}'.format(basket.order['payment']))

        basket.logger.info('\nРеквизиты покупателя: {}'.format(basket.order['customer']))

        return JsonResponseUTF8(response)
