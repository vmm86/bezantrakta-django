import logging
import uuid
from mail_templated import EmailMessage

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.db.models import F
from django.shortcuts import redirect

from project.cache import cache_factory
from project.shortcuts import message, render_messages, timezone_now

from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS
from bezantrakta.eticket.shortcuts import render_eticket


def payment_success(request):
    """Обработка успешного результата оплаты."""
    logger = logging.getLogger('bezantrakta.order')

    event_uuid = uuid.UUID(request.GET.get('event_uuid'))
    order_uuid = uuid.UUID(request.GET.get('order_uuid'))

    now = timezone_now()
    logger.info('\n----------Обработка успешной оплаты заказа {order_uuid}----------'.format(order_uuid=order_uuid))
    logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

    event = cache_factory('event', event_uuid)
    if event is None:
        # Сообщение об ошибке
        msgs = [
            message('error', 'К сожалению, такого события не существует. 😞'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')
    event['id'] = event['ticket_service_event']
    # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
    logger.info('Событие')
    logger.info(event)

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

        # Настройки сервиса продажи билетов
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        # Экземпляр класса сервиса продажи билетов
        ts = ticket_service['instance']

        # Настройки сервиса онлайн-оплаты
        payment_service = cache_factory('payment_service', event['payment_service_id'])
        # Экземпляр класса сервиса онлайн-оплаты
        ps = payment_service['instance']

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
            logger.info('Статус заказа: {status}\n'.format(
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
            from_email['user'] = ticket_service['settings']['order_email']['user']
            from_email['pswd'] = ticket_service['settings']['order_email']['pswd']
            from_email['connection'] = EmailBackend(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=from_email['user'],
                password=from_email['pswd'],
                use_tls=settings.EMAIL_USE_TLS,
            )

            email_context = {
                'domain': domain,
                'event': event,
                'ticket_service': ticket_service,
                'payment_service': payment_service,
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
                    t.update(event)
                    # logger.info('\nКонтекст билета')
                    # logger.info(t)
                    pdf_ticket_file = render_eticket(t)
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
                        event_url=event['url'])
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')
