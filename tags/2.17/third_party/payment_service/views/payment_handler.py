import logging
import uuid

from django.db.models import F
from django.shortcuts import redirect

from project.cache import cache_factory
from project.shortcuts import message, render_messages, timezone_now

from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.shortcuts import success_or_error


def payment_handler(request):
    """Проверка и обработка успешной или НЕуспешной оплаты."""
    logger = logging.getLogger('bezantrakta.order')

    event_uuid = uuid.UUID(request.GET.get('event_uuid', None))
    order_uuid = uuid.UUID(request.GET.get('order_uuid', None))

    # Если статус оплаты приходит сразу в GET-парамерах
    # (возможный обходной вариант для сервисов, у которых нельзя запросить статус оплаты отдельным запросом)
    success = request.GET.get('success', None)
    payment_id = request.GET.get('payment_id', None)
    error_code = request.GET.get('error_code', None)
    error_message = request.GET.get('error_message', None)

    # Сообщение об ошибке при НЕполучении необходимых для обработки данных
    if not event_uuid or not order_uuid:
        msgs = [
            message('error', 'К сожалению, такого заказа не существует. 😞'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')

    now = timezone_now()
    logger.info('\n----------Обработка оплаты заказа {order_uuid}----------'.format(order_uuid=order_uuid))
    logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

    event = cache_factory('event', event_uuid)
    event['id'] = event['ticket_service_event']
    logger.info('Событие')
    logger.info(event)

    # Получение параметров заказа из БД
    try:
        order = dict(Order.objects.annotate(
            event_uuid=F('event'),
            event_id=F('ticket_service_event'),
            order_uuid=F('id'),
            order_id=F('ticket_service_order'),
        ).values(
            'event_uuid',
            'event_id',
            'order_uuid',
            'order_id',
            'ticket_service_id',
            'name',
            'email',
            'phone',
            'delivery',
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
            order['tickets'] = list(OrderTicket.objects.annotate(
                ticket_id=F('id'),
            ).values(
                'ticket_id',
                'ticket_service_order',
                'bar_code',
                'sector_id',
                'sector_title',
                'row_id',
                'seat_id',
                'seat_title',
                'price_group_id',
                'price'
            ).filter(
                order_id=order_uuid
            ))
        except OrderTicket.DoesNotExist:
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, в заказе нет ни одного билета - бронь на билеты истекла. 😞'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['url'])
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')
    except Order.DoesNotExist:
        # Сообщение об ошибке
        msgs = [
            message('error', 'К сожалению, такой заказ ещё не был создан. 😞'),
            message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                    event_url=event['url'])
                    ),
        ]
        render_messages(request, msgs)
        return redirect('error')
    else:
        logger.info('\nЗаказ')
        logger.info(order)
        logger.info('\nБилеты в заказе')
        logger.info(order['tickets'])

        # Настройки сервиса онлайн-оплаты
        payment_service = cache_factory('payment_service', event['payment_service_id'])
        # Экземпляр класса сервиса онлайн-оплаты
        ps = payment_service['instance']

        # Если статус оплаты требуется запросить отдельно
        if success is None:
            # Проверка статуса оплаты
            payment_status = ps.payment_status(payment_id=order['payment_id'])
        # Если статус оплаты приходит сразу в GET-парамерах
        else:
            payment_status = {}
            payment_status['success'] = success
            payment_status['payment_id'] = payment_id
            payment_status['error_code'] = error_code
            payment_status['error_message'] = error_message

        logger.info('payment_status: {}'.format(payment_status))

        # Обработка успешной или НЕуспешной оплаты
        result = success_or_error(request, payment_status, order, event)

        # Если оплата завершилась успешно - редирект на шаг 3 с информацией о заказе
        if result:
            return redirect('order:confirmation', order_uuid=order['order_uuid'])
        # Если оплата завершилась НЕуспешно - редирект на страницу с информацией об ошибке
        else:
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, в процессе оплаты возникла ошибка. 😞'),
                message('error', '{code} {message}'.format(
                        code=payment_status['error_code'],
                        message=payment_status['error_message'])
                        ),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['url'])
                        ),
            ]
            render_messages(request, msgs)

            return redirect('error')
