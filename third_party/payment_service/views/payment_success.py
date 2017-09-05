import logging
import uuid
from mail_templated import EmailMessage

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.db.models import F
from django.shortcuts import redirect

from project.shortcuts import message, render_messages, timezone_now

from bezantrakta.event.shortcuts import add_small_vertical_poster
from bezantrakta.event.cache import get_or_set_cache as get_or_set_event_cache

from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS

from bezantrakta.eticket.shortcuts import render_ticket

from third_party.payment_service.cache import get_or_set_cache as get_or_set_payment_service_cache
from third_party.payment_service.cache import payment_service_instance

from third_party.ticket_service.cache import get_or_set_cache as get_or_set_ticket_service_cache
from third_party.ticket_service.cache import ticket_service_instance


def payment_success(request):
    """Обработка успешного результата оплаты."""
    logger = logging.getLogger('bezantrakta.order')

    event_uuid = uuid.UUID(request.GET.get('event_uuid'))
    order_uuid = uuid.UUID(request.GET.get('order_uuid'))

    logger.info('\n----------Обработка успешной оплаты заказа {order_uuid}----------'.format(order_uuid=order_uuid))

    event = {}
    event['info'] = get_or_set_event_cache(event_uuid)
    event['id'] = event['info']['ticket_service_event']
    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    add_small_vertical_poster(request, event['info'])
    logger.info('Событие')
    logger.info(event['info'])

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
        logger.info('\nБилеты в заказе')
        logger.info(order['tickets'])

        # Получение параметров сайта
        domain = {}
        domain['id'] = request.domain_id
        domain['title'] = request.domain_title
        domain['slug'] = request.domain_slug
        domain['url'] = request.url_domain
        domain['settings'] = request.domain_settings

        # Получение реквизитов покупателя
        customer = {}
        customer['delivery'] = order['delivery']
        customer['payment'] = order['payment']
        customer['name'] = order['name']
        customer['email'] = order['email']
        customer['phone'] = order['phone']

        # Проверка корректности `order_id`
        # Если билеты сменили статус на `SOL` при том, что сохранили сессию и номер брони - они были выкуплены в кассе.
        # reservation_timed_out = check_order_id(tickets, order['order_id'])
        # if (reservation_timed_out == false)
        #     order['payment_info']['code'] = ''
        #     order['payment_info']['message'] = 'reservation ' + order['order_id'] + ' timed out'

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

        # Если оплата прошла успешно
        if payment_status['success']:
            logger.info('\nОплата {payment_id} завершилась успешно'.format(payment_id=order['payment_id']))

            payment_datetime = timezone_now()

            # Подтверждение оплаты в сервисе продажи билетов
            order_payment = ts.order_payment(
                event_id=event['id'],
                order_uuid=order_uuid,
                order_id=order['order_id'],
                payment_id=order['payment_id'],
                payment_datetime=payment_datetime,
                tickets=order['tickets'],
            )
            if order_payment['success']:
                logger.info('Заказ {order_id} в сервисе продажи билетов отмечен как оплаченный'.format(
                    order_id=order['order_id']
                    )
                )
            else:
                logger.info('Заказ {order_id} не удалось отметить в сервисе продажи билетов как оплаченный'.format(
                    order_id=order['order_id']
                    )
                )

            # Подтверждение оплаты заказа в БД
            order['status'] = 'approved'
            logger.info('Статус заказа: {status}'.format(
                status=ORDER_STATUS[order['status']]['description'])
            )

            Order.objects.filter(id=order_uuid).update(status=order['status'])

            # Человекопонятный текст для email-уведомлений
            customer['delivery_description'] = ORDER_DELIVERY[customer['delivery']]
            customer['payment_description'] = ORDER_PAYMENT[customer['payment']]
            customer['status_color'] = ORDER_STATUS[order['status']]['color']
            customer['status_description'] = ORDER_STATUS[order['status']]['description']

            # Отправка email администратору и покупателю
            from_email = {}
            from_email['user'] = ticket_service['info']['settings']['order_email']['user']
            from_email['pswd'] = ticket_service['info']['settings']['order_email']['pswd']
            from_email['connection'] = EmailBackend(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=from_email['user'],
                password=from_email['pswd'],
                use_tls=settings.EMAIL_USE_TLS,
            )

            email_context = {
                'domain': domain,
                'event': event['info'],
                'ticket_service': ticket_service['info'],
                'payment_service': payment_service['info'],
                'order': order,
                'customer': customer
            }

            admin_email = EmailMessage(
                'order/email_admin.tpl',
                email_context,
                from_email['user'],
                (from_email['user'],),
                connection=from_email['connection']
            )
            customer_email = EmailMessage(
                'order/email_customer.tpl',
                email_context,
                from_email['user'],
                (customer['email'],),
                connection=from_email['connection']
            )

            # Опциональная генерация электронных билетов и их вложение в письмо покупателю
            if customer['delivery'] == 'email':
                for t in order['tickets']:
                    t.update(event['info'])
                    logger.info('Контекст билета')
                    logger.info(t)
                    pdf_ticket_file = render_ticket(t)
                    customer_email.attach_file(pdf_ticket_file, mimetype='application/pdf')

            admin_email.send()
            logger.info('Email-уведомление администратору отправлено')
            customer_email.send()
            logger.info('Email-уведомление покупателю отправлено')

            return redirect('order:confirmation', order_uuid=order_uuid)
        # Если оплата прошла НЕуспешно
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

            Order.objects.filter(id=order['uuid']).update(status=order['status'])

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
