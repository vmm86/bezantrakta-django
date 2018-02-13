import logging
import uuid

from django.db.models import F
from django.shortcuts import redirect

from project.cache import cache_factory
from project.shortcuts import BOOLEAN_VALUES, message, render_messages, timezone_now

from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.shortcuts import success_or_error


def payment_handler(request):
    """Проверка и обработка успешной или НЕуспешной оплаты после возвращения с формы онлайн-оплаты."""
    logger = logging.getLogger('bezantrakta.order')

    # Получение уникальных идентификаторов события и заказа из GET-парамеров
    event_uuid = request.GET.get('event_uuid', None)
    if event_uuid is not None:
        try:
            event_uuid = uuid.UUID(event_uuid)
        except ValueError:
            event_uuid = None

    order_uuid = request.GET.get('order_uuid', None)
    if order_uuid is not None:
        try:
            order_uuid = uuid.UUID(order_uuid)
        except ValueError:
            order_uuid = None

    # Сообщение об ошибке при НЕполучении необходимых для обработки данных
    if event_uuid is None or order_uuid is None:
        msgs = [
            message('error', 'К сожалению, произошла ошибка - такого заказа не существует. 🙁'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')

    # Попытка получить статус оплаты сразу из GET-парамеров
    # (возможный обходной вариант для сервисов, у которых нельзя запросить статус оплаты отдельным запросом)
    success = request.GET.get('success', None)
    payment_id = request.GET.get('payment_id', None)
    error_code = request.GET.get('code', None)
    error_message = request.GET.get('message', None)

    if success is not None:
        success = True if success in BOOLEAN_VALUES else False

    # Логирование информации об обработке
    now = timezone_now()
    logger.info('\n----------Обработка оплаты заказа {order_uuid}----------'.format(order_uuid=order_uuid))
    logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

    # Получение параметров сайта
    domain = cache_factory('domain', request.domain_slug)

    # Получение параметров события
    event = cache_factory('event', event_uuid)
    event['id'] = event['ticket_service_event']
    logger.info('Событие:')
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
            'total',
            'overall'
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
                'price'
            ).filter(
                order_id=order_uuid
            ))
        except OrderTicket.DoesNotExist:
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, в заказе нет ни одного билета - предварительный резерв истёк. 🙁'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['url'])
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')
    except Order.DoesNotExist:
        # Сообщение об ошибке
        msgs = [
            message('error', 'К сожалению, такой заказ не был создан. 🙁'),
            message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                    event_url=event['url'])
                    ),
        ]
        render_messages(request, msgs)
        return redirect('error')
    else:
        logger.info('\nЗаказ:')
        logger.info(order)
        logger.info('\nБилеты в заказе:')
        logger.info(order['tickets'])

        # Настройки сервиса онлайн-оплаты
        payment_service = cache_factory('payment_service', event['payment_service_id'])
        # Экземпляр класса сервиса онлайн-оплаты
        ps = payment_service['instance']

        # Если статус оплаты не получен сразу и его требуется запросить отдельно
        if success is None:
            # Проверка статуса оплаты
            payment_status = ps.payment_status(payment_id=order['payment_id'])
        # Если статус оплаты приходит сразу в GET-парамерах
        else:
            payment_status = {}
            payment_status['success'] = success
            payment_status['payment_id'] = payment_id
            payment_status['code'] = error_code
            payment_status['message'] = error_message

            # Сообщение об ошибке при НЕполучении идентификатора оплаты
            if payment_status['payment_id'] is None:
                msgs = [
                    message('error', 'К сожалению, произошла ошибка - такая оплата не проводилась. 🙁'),
                    message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                            event_url=event['url'])
                            ),
                ]
                render_messages(request, msgs)
                return redirect('error')

        logger.info('Статус оплаты:')
        logger.info(payment_status)

        # Обработка успешной или НЕуспешной оплаты
        result = success_or_error(domain, event, order, payment_status, logger)

        # Если оплата завершилась успешно - редирект на шаг 3 с информацией о заказе
        if result['success']:
            return redirect('order:confirmation', order_uuid=order['order_uuid'])
        # Если оплата завершилась НЕуспешно - редирект на страницу с информацией об ошибке
        else:
            # Сборка очереди сообщений для вывода на странице ошибки
            msgs = []
            for item in result['messages']:
                msgs.append(message(item['level'], item['message']))

            render_messages(request, msgs)

            return redirect('error')
