import logging
import uuid

from django.db.models import F
from django.shortcuts import redirect

from project.shortcuts import message, render_messages

from bezantrakta.event.cache import get_or_set_cache as get_or_set_event_cache
from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS

from third_party.payment_service.cache import get_or_set_cache as get_or_set_payment_service_cache
from third_party.payment_service.cache import payment_service_instance

from third_party.ticket_service.cache import get_or_set_cache as get_or_set_ticket_service_cache
from third_party.ticket_service.cache import ticket_service_instance


def payment_error(request):
    """Обработка НЕуспешного результата оплаты."""
    logger = logging.getLogger('bezantrakta.order')

    event_uuid = uuid.UUID(request.GET.get('event_uuid'))
    order_uuid = uuid.UUID(request.GET.get('order_uuid'))

    logger.info('\n----------Обработка НЕуспешной оплаты заказа {order_uuid}----------'.format(order_uuid=order_uuid))

    event = {}
    event['info'] = get_or_set_event_cache(event_uuid)
    event['id'] = event['info']['ticket_service_event']
    # logger.info('Событие')
    # logger.info(event['info'])

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
            order['tickets'] = list(OrderTicket.objects.filter(order_id=order_uuid).values())
        except OrderTicket.DoesNotExist:
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, в заказе нет ни одного билета - бронь на билеты истекла. 😞'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['info']['url'])
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')
    except Order.DoesNotExist:
        # Сообщение об ошибке
        msgs = [
            message('error', 'К сожалению, такой заказ ещё не был создан. 😞'),
            message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                    event_url=event['info']['url'])
                    ),
        ]
        render_messages(request, msgs)
        return redirect('error')
    else:
        logger.info('\nЗаказ')
        logger.info(order)

        # Экземпляр класса сервиса продажи билетов
        ticket_service = {}
        ticket_service['id'] = event['info']['ticket_service_id']
        ticket_service['info'] = get_or_set_ticket_service_cache(ticket_service['id'])

        ts = ticket_service_instance(ticket_service['id'])

        # Экземпляр класса сервиса онлайн-оплаты
        payment_service = {}
        payment_service['id'] = event['info']['payment_service_id']
        payment_service['info'] = get_or_set_payment_service_cache(payment_service['id'])

        ps = payment_service_instance(payment_service['id'])

        # Проверка статуса оплаты
        payment_status = ps.payment_status(payment_id=order['payment_id'])

        if payment_status['success']:
            logger.info('\nОплата {payment_id} завершилась успешно'.format(payment_id=order['payment_id']))
            return redirect('payment:payment_success')
        else:
            logger.info('\nОплата {payment_id} завершилась НЕуспешно'.format(payment_id=order['payment_id']))

            # Отмена заказа в сервисе продажи билетов
            ts.order_delete(
                event_id=event['id'],
                order_uuid=order_uuid,
                order_id=order['order_id'],
                tickets=order['tickets'],
            )

            # Отмена заказа в БД
            order['status'] = 'cancelled'
            logger.info('Статус заказа: {status}'.format(
                status=ORDER_STATUS[order['status']]['description'])
            )

            Order.objects.filter(id=order_uuid).update(status=order['status'])

            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, в процессе оплаты возникла ошибка. 😞'),
                message('error', '{code} {message}'.format(
                        code=payment_status['code'],
                        message=payment_status['message'])
                        ),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['info']['url'])
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')
