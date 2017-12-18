import uuid

from django.db.models import F
from django.shortcuts import redirect, render

from project.cache import cache_factory
from project.shortcuts import message, render_messages

from ..models import Order, OrderTicket
from ..settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS


def confirmation(request, order_uuid):
    """Вывод информации об успешном или НЕуспешном заказе.

    Args:
        order_uuid (str): Уникальный идентификатор заказа.
    """
    try:
        order_uuid = uuid.UUID(order_uuid)
    except (AttributeError, TypeError, ValueError):
        # Сообщение об ошибке
        msgs = [
            message('error', 'Введён некорректный идентификатор заказа. 😞'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')
    else:
        # Получение параметров заказа из БД
        try:
            order = dict(Order.objects.annotate(
                event_uuid=F('event'),
                event_id=F('ticket_service_event'),
                order_id=F('ticket_service_order'),
            ).values(
                'event_uuid',
                'event_id',
                'order_id',
                'ticket_service_id',
                'delivery',
                'address',
                'payment',
                'payment_id',
                'status',
                'tickets_count',
                'total'
            ).get(
                id=order_uuid,
            ))
            # Получение билетов в заказе
            try:
                order_tickets = list(OrderTicket.objects.filter(order_id=order_uuid).values())
            except OrderTicket.DoesNotExist:
                # Сообщение об ошибке
                msgs = [
                    message('error', 'В заказе нет ни одного билета. 😞'),
                    message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
                ]
                render_messages(request, msgs)
                return redirect('error')
        except Order.DoesNotExist:
            # Сообщение об ошибке
            msgs = [
                message('warning', 'К сожалению, такого заказа не существует. 😞'),
                message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
            ]
            render_messages(request, msgs)
            return redirect('error')
        else:
            # Информация о событии из кэша
            event = cache_factory('event', order['event_uuid'])

            # Информация о сервисе продажи билетов
            ticket_service = cache_factory('ticket_service', event['ticket_service_id'])

            # Информация о сервисе онлайн-оплаты
            payment_service = cache_factory('payment_service', event['payment_service_id'])
            # Экземпляр класса сервиса онлайн-оплаты
            ps = payment_service['instance']

            if order['delivery'] == 'courier':
                # Стоимость доставки курьером
                order['courier_price'] = ps.decimal_price(ticket_service['settings']['courier_price'])

            if order['payment'] == 'online':
                # Комиссия сервиса онлайн-оплаты
                order['commission'] = ps.decimal_price(payment_service['settings']['init']['commission'])

            # Вывод основной информации о заказе
            order_info = []
            order_info.append({'key': 'Номер заказа:', 'value': order['order_id']})

            order_info.append({
                'key': 'Статус заказа:',
                'value': '<span style="color: {color};">{description}</span>'.format(
                    color=ORDER_STATUS[order['status']]['color'],
                    description=ORDER_STATUS[order['status']]['description'],
                )
            })
            order_info.append({'key': 'Получение:', 'value': ORDER_DELIVERY[order['delivery']]})
            if order['delivery'] == 'courier':
                order_info.append({'key': 'Адрес доставки:', 'value': order['address']})
            order_info.append({'key': 'Оплата:',    'value': ORDER_PAYMENT[order['payment']]})

            if order['payment'] == 'online' and order['status'] == 'approved':
                order_info.append({'key': 'Номер оплаты:', 'value': order['payment_id']})

            context = {}

            context['event'] = event
            context['order'] = order
            context['order']['tickets'] = order_tickets
            context['order']['info'] = order_info

            return render(request, 'order/confirmation.html', context)