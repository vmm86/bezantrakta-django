import logging
import simplejson as json
import uuid

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket
from bezantrakta.order.settings import ORDER_TYPE

from api.shortcuts import JsonResponseUTF8


def change_type(request):
    if request.is_ajax() and request.method == 'POST':
        logger = logging.getLogger('bezantrakta.reserve')

        customer = request.POST.get('customer', None)
        try:
            customer = json.loads(customer)
        except (TypeError, ValueError):
            response = {'success': False, 'message': 'Реквизиты покупателя некорректны или отсутствуют'}
            return JsonResponseUTF8(response)
        else:
            if type(customer) is not dict:
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
        else:
            if order_type not in ORDER_TYPE:
                response = {'success': False, 'message': 'Получен некорректный тип заказа'}
                return JsonResponseUTF8(response)

        # Получение существующего предварительного резерва
        basket = OrderBasket(order_uuid=order_uuid)
        if not basket.order:
            response = {'success': False, 'message': 'Отсутствует предварительный резерв с указанным UUID'}
            return JsonResponseUTF8(response)

        # Информация о событии, UUID которого сохранён в предварительном резерве
        event = cache_factory('event', basket.order['event_uuid'])
        if not event:
            response = {'success': False, 'message': 'Отсутствует событие с указанным UUID'}
            return JsonResponseUTF8(response)

        # Изменение типа получения и оплаты билетов в предварительном резерве
        basket.change_order_type(customer, order_type)

        response = {}
        response['success'] = True
        response['order'] = basket.order

        # Получение параметров сайта
        domain = cache_factory('domain', request.domain_slug)

        logger.info('\n----------change_order_type----------')
        logger.info('{:%Y-%m-%d %H:%M:%S}'.format(timezone_now()))
        logger.info('Сайт: {}'.format(domain['domain_title']))

        logger.info('order_uuid: {}'.format(order_uuid))
        logger.info('order_type: {}'.format(order_type))
        logger.info('order: {}'.format(basket.order))

        return JsonResponseUTF8(response)
