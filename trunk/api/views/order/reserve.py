from project.shortcuts import BOOLEAN_VALUES, timezone_now

from bezantrakta.order.order_basket import OrderBasket

from api.shortcuts import JsonResponseUTF8


def reserve(request):
    """Добавление или удаление места в предварительном резерве."""
    if request.is_ajax() and request.method == 'POST':
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

        is_fixed = request.POST.get('is_fixed', None)
        is_fixed = True if is_fixed in BOOLEAN_VALUES else False

        action = request.POST.get('action', 'add')

        # Получение существующего ранее инициализированного предварительного резерва
        basket = OrderBasket(order_uuid=order_uuid)

        if not basket or not basket.order:
            response = {'success': False, 'message': 'Отсутствует предварительный резерв с указанным UUID'}
            return JsonResponseUTF8(response)

        basket.logger.info('\n----------Добавление/удаление билета в предварительном резерве----------')
        basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

        basket.logger.info('\nПредыдущее состояние заказа:')
        if basket.order['tickets']:
            basket.logger.info('    Билеты в заказе:')
            for tid, t in basket.order['tickets'].items():
                basket.logger.info('    * {}: {}'.format(tid, t))
        else:
            basket.logger.info('    Билеты в заказе: []')
        basket.logger.info('    Число билетов: {}'.format(basket.order['tickets_count']))
        basket.logger.info('    Сумма цен на билеты: {}'.format(basket.order['total']))

        # Добавление или удаление билета в предварительном резерве
        response = basket.ticket_toggle(ticket_id, is_fixed, action)

        if (action == 'add' and response['success']) or action == 'remove':
            basket.logger.info('\nПоследующее состояние заказа:')
            if basket.order['tickets']:
                basket.logger.info('    Билеты в заказе:')
                for tid, t in basket.order['tickets'].items():
                    basket.logger.info('    * {}: {}'.format(tid, t))
            else:
                basket.logger.info('    Билеты в заказе: []')
            basket.logger.info('    Число билетов: {}'.format(basket.order['tickets_count']))
            basket.logger.info('    Сумма цен на билеты: {}'.format(basket.order['total']))

        return JsonResponseUTF8(response)
