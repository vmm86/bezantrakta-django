from mail_templated import EmailMessage

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend

from project.cache import cache_factory
from project.shortcuts import build_absolute_url, timezone_now

from bezantrakta.eticket.shortcuts import render_eticket

from .models import Order
from .settings import ORDER_DELIVERY_CAPTION, ORDER_PAYMENT_CAPTION, ORDER_STATUS_CAPTION


def success_or_error(domain, event, order, payment_status, logger):
    """Обработка успешной или НЕуспешной оплаты.

    Args:
        domain (dict): Информация о сайте.
        event (dict): Информация о событии.
        order (dict): Информация о заказе.
        payment_status (dict): Информация о сервисе онлайн-оплаты.
        logger (logging.Logger): Файл для логирования процесса завершения заказа.

    Returns:
        dict: Словарь ``result`` с информацией об успешном или НЕуспешном завершении заказа с онлайн-оплатой.

            Содержимое ``result``:
                * **success** (bool): Успешное (``True``) или НЕуспешное (``False``) завершение заказа.
                * **messages** (list): Сообщения для последующего использования. В случае успешного завершения заказа - пустой список, в случае НЕуспешного завершения заказа - список из словарей с ключами ``level`` (уровень ошибки) и ``message`` (сообщение об ошибке).
    """
    # Заготовка для последующего возарата успешного или НЕуспешного ответа
    result = {}
    result['success'] = None
    result['messages'] = []

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

    # Тип заказа
    order['type'] = '{delivery}_{payment}'.format(delivery=order['delivery'], payment=order['payment'])
    # Процент сервисного сбора
    order['extra'] = event['settings']['extra'][order['type']]

    # Если оплата завершилась успешно
    if payment_status['success']:
        logger.info('\nОплата {payment_id} завершилась успешно'.format(payment_id=order['payment_id']))

        # Подтверждение оплаты в сервисе продажи билетов
        logger.info('Подтверждение оплаты заказа в сервисе продажи билетов...')
        order_approve = ts.order_approve(
            event_id=event['id'],
            order_uuid=order['order_uuid'],
            order_id=order['order_id'],
            payment_id=order['payment_id'],
            payment_datetime=timezone_now(),
            tickets=order['tickets'],
        )
        logger.info(order_approve)
        # Заказ успешно подтверждён как оплаченный в сервисе продажи билетов
        if order_approve['success']:
            result['success'] = True

            logger.info('Заказ {order_id} в сервисе продажи билетов отмечен как оплаченный'.format(
                order_id=order['order_id']
                )
            )

            # Подтверждение оплаты заказа в БД
            order['status'] = 'approved'
            Order.objects.filter(id=order['order_uuid']).update(status=order['status'])

            logger.info('Статус заказа: {status}\n'.format(
                status=ORDER_STATUS_CAPTION[order['status']]['description'])
            )

            # Человекопонятный текст для email-уведомлений
            customer['delivery_description'] = ORDER_DELIVERY_CAPTION[customer['delivery']]
            customer['payment_description'] = ORDER_PAYMENT_CAPTION[customer['payment']]
            customer['status_color'] = ORDER_STATUS_CAPTION[order['status']]['color']
            customer['status_description'] = ORDER_STATUS_CAPTION[order['status']]['description']

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
                logger.info('\nСоздание электронных PDF-билетов...')
                for ticket in order['tickets']:
                    ticket.update(event)
                    logger.info('\nИнформация о билете:')
                    logger.info(ticket)
                    pdf_ticket_file = render_eticket(ticket, logger)
                    customer_email.attach_file(pdf_ticket_file, mimetype='application/pdf')

            admin_email.send()
            logger.info('Email-уведомление администратору отправлено')
            customer_email.send()
            logger.info('Email-уведомление покупателю отправлено')
        # Заказ НЕ удалось подтвердить как оплаченный в сервисе продажи билетов
        else:
            result['success'] = False

            logger.info('Заказ {order_id} НЕ удалось отметить в сервисе продажи билетов как оплаченный'.format(
                order_id=order['order_id']
                )
            )

            # Сообщения для вывода на странице или в лог-файле
            messages = [
                {
                    'level': 'error',
                    'message': 'К сожалению, ваш заказ {order_id} не смог завершиться успешно. 🙁'.format(
                        order_id=order['order_id']
                    )
                },
                {
                    'level': 'info',
                    'message': 'Заказ будет завершён в ближайшее время с отправкой уведомления на указанный вами email.'
                },
                {
                    'level': 'info',
                    'message': 'Если подтверждения не последует - <a href="{contacts_url}" target="_blank">свяжитесь с администратором сайта</a>.'.format(
                        contacts_url=build_absolute_url(domain['domain_slug'], '/kontakty/')
                    )
                },
                {
                    'level': 'info',
                    'message': '👉 <a href="/">Перейти на главную</a>.'.format(
                        event_url=event['url']
                    )
                },
            ]

            for msg in messages:
                result['messages'].append(msg)

        return result
    # Если оплата завершилась НЕуспешно
    else:
        logger.info('\nОплата {payment_id} завершилась НЕуспешно'.format(payment_id=order['payment_id']))

        result['success'] = False

        # Отмена заказа в сервисе продажи билетов
        logger.info('Отмена заказа в сервисе продажи билетов...')
        order_cancel = ts.order_cancel(
            event_id=event['id'],
            order_uuid=order['order_uuid'],
            order_id=order['order_id'],
            tickets=order['tickets'],
        )
        logger.info(order_cancel)
        # Заказ успешно отмечен как отменённый в сервисе продажи билетов
        if order_cancel['success']:
            logger.info('Заказ {order_id} отменён в сервисе продажи билетов'.format(
                order_id=order['order_id']
                )
            )

            # Отмена заказа в БД
            order['status'] = 'cancelled'
            Order.objects.filter(id=order['order_uuid']).update(status=order['status'])

            logger.info('Статус заказа: {status}'.format(
                status=ORDER_STATUS_CAPTION[order['status']]['description'])
            )
        # Заказ НЕ удалось отметить как отменённый в сервисе продажи билетов
        else:
            logger.info('Заказ {order_id} НЕ удалось отменить в сервисе продажи билетов'.format(
                order_id=order['order_id']
                )
            )

        # Сообщения об ошибке для вывода на странице или в лог-файле
        messages = [
            {'level': 'error', 'message': 'К сожалению, в процессе оплаты возникла ошибка. 🙁'},
            {'level': 'error', 'message': '{code} {message}'.format(
                code=payment_status['code'],
                message=payment_status['message']
            )},
            {'level': 'info',  'message': '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                event_url=event['url']
            )},
        ]

        for msg in messages:
            result['messages'].append(msg)

        return result
