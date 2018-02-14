import uuid

from django.db.models import F
from django.shortcuts import redirect, render

from project.cache import cache_factory
from project.shortcuts import message, render_messages

from ..models import Order, OrderTicket
from ..settings import ORDER_DELIVERY_CAPTION, ORDER_PAYMENT_CAPTION, ORDER_STATUS_CAPTION


def order_step_3(request, order_uuid):
    """Вывод информации об успешном или НЕуспешном заказе.

    Args:
        order_uuid (str): Уникальный идентификатор заказа.
    """
    try:
        order_uuid = uuid.UUID(order_uuid)
    except (AttributeError, TypeError, ValueError):
        # Сообщение об ошибке
        msgs = [
            message('error', 'Введён некорректный идентификатор заказа. 🙁'),
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
                    message('error', 'В заказе нет ни одного билета. 🙁'),
                    message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
                ]
                render_messages(request, msgs)
                return redirect('error')
        except Order.DoesNotExist:
            # Сообщение об ошибке
            msgs = [
                message('warning', 'К сожалению, такого заказа не существует. 🙁'),
                message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
            ]
            render_messages(request, msgs)
            return redirect('error')
        else:
            # Информация о событии из кэша
            event = cache_factory('event', order['event_uuid'])

            # Информация о сервисе продажи билетов и экземпляр класса сервиса продажи билетов
            ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
            # Экземпляр класса сервиса продажи билетов
            ts = ticket_service['instance']

            # Информация о сервисе онлайн-оплаты
            payment_service = cache_factory('payment_service', event['payment_service_id'])
            # Экземпляр класса сервиса онлайн-оплаты
            ps = payment_service['instance'] if payment_service is not None else None

            # Тип заказа
            order['type'] = '{delivery}_{payment}'.format(delivery=order['delivery'], payment=order['payment'])

            # Процент сервисного сбора
            order['extra'] = event['settings']['extra'][order['type']]
            # Стоимость доставки курьером
            order['courier_price'] = ts.decimal_price(ticket_service['settings']['courier_price'])
            # Комиссия сервиса онлайн-оплаты
            order['commission'] = (
                ps.decimal_price(payment_service['settings']['init']['commission']) if
                payment_service is not None else
                ts.decimal_price(0)
            )

            # Формирование заголовка для общей суммы заказа
            order['overall_header'] = 'Всего с учётом сервисного сбора' if order['extra'] > 0 else 'Общая сумма заказа'

            if order['delivery'] == 'courier':
                if order['courier_price'] > 0:
                    order['overall_header'] = (
                        'Всего с учётом доставки курьером и сервисного сбора' if
                        order['extra'] > 0 else
                        'Всего с учётом доставки курьером'
                    )
            if order['payment'] == 'online':
                if order['commission'] > 0:
                    order['overall_header'] = (
                        'Всего с учётом комиссии платёжной системы и сервисного сбора' if
                        order['extra'] > 0 else
                        'Всего с учётом комиссии платёжной системы'
                    )
                else:
                    order['overall_header'] = (
                        'Всего с учётом комиссии платёжной системы и сервисного сбора' if
                        order['extra'] > 0 else
                        'Общая сумма заказа'
                    )

            # Вывод основной информации о заказе
            order_info = []
            order_info.append({'key': 'Номер заказа:', 'value': order['order_id']})

            order_info.append({
                'key': 'Статус заказа:',
                'value': '<span style="color: {color};">{description}</span>'.format(
                    color=ORDER_STATUS_CAPTION[order['status']]['color'],
                    description=ORDER_STATUS_CAPTION[order['status']]['description'],
                )
            })
            order_info.append({'key': 'Получение:', 'value': ORDER_DELIVERY_CAPTION[order['delivery']]})
            if order['delivery'] == 'courier':
                order_info.append({'key': 'Адрес доставки:', 'value': order['address']})
            order_info.append({'key': 'Оплата:',    'value': ORDER_PAYMENT_CAPTION[order['payment']]})

            if order['payment'] == 'online' and order['status'] == 'approved':
                order_info.append({'key': 'Номер оплаты:', 'value': order['payment_id']})

            context = {}

            context['event'] = event
            context['order'] = order
            context['order']['tickets'] = order_tickets
            context['order']['info'] = order_info

            return render(request, 'order/order_step_3.html', context)
