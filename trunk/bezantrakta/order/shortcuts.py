import logging
from mail_templated import EmailMessage

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.eticket.shortcuts import render_eticket

from bezantrakta.order.models import Order
from bezantrakta.order.settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS


def success_or_error(domain, event, order, payment_status):
    """Обработка успешной или НЕуспешной оплаты.

    Args:
        domain (dict): Информация о сайте.
        event (dict): Информация о событии.
        order (dict): Информация о заказе.
        payment_status (dict): Информация о сервисе онлайн-оплаты.

    Returns:
        dict: Словарь ``result`` с информацией об успешном или НЕуспешном завершении заказа с онлайн-оплатой.

            Содержимое ``result``:
                * **success** (bool): Успешное (``True``) или НЕуспешное (``False``) завершение заказа.
                * **messages** (list): Сообщения для последующего использования в случае НЕуспешного завершения заказа. Список из словарей с ключами ``level`` (уровень ошибки) и ``message`` (сообщение об ошибке).
    """
    # Заготовка для последующего возарата успешного или НЕуспешного ответа
    result = {}
    result['success'] = None
    result['messages'] = []

    logger = logging.getLogger('bezantrakta.order')

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

    # Если оплата завершилась успешно
    if payment_status['success']:
        logger.info('\nОплата {payment_id} завершилась успешно'.format(payment_id=order['payment_id']))

        # Подтверждение оплаты в сервисе продажи билетов
        logger.info('Подтверждение оплаты заказа в сервисе продажи билетов...')
        order_payment = ts.order_payment(
            event_id=event['id'],
            order_uuid=order['order_uuid'],
            order_id=order['order_id'],
            payment_id=order['payment_id'],
            payment_datetime=timezone_now(),
            tickets=order['tickets'],
        )
        # Заказ успешно подтверждён как оплаченный в сервисе продажи билетов
        if order_payment['success']:
            result['success'] = True

            logger.info('Заказ {order_id} в сервисе продажи билетов отмечен как оплаченный'.format(
                order_id=order['order_id']
                )
            )

            # Подтверждение оплаты заказа в БД
            order['status'] = 'approved'
            Order.objects.filter(id=order['order_uuid']).update(status=order['status'])

            logger.info('Статус заказа: {status}\n'.format(
                status=ORDER_STATUS[order['status']]['description'])
            )

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
                logger.info('\nСоздание электронных PDF-билетов...')
                for t in order['tickets']:
                    t.update(event)
                    # logger.info('\nИнформация о билете:')
                    # logger.info(t)
                    pdf_ticket_file = render_eticket(t)
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

        return result
    # Если оплата завершилась НЕуспешно
    else:
        logger.info('\nОплата {payment_id} завершилась НЕуспешно'.format(payment_id=order['payment_id']))

        result['success'] = False

        # Отмена заказа в сервисе продажи билетов
        logger.info('Отмена заказа в сервисе продажи билетов...')
        order_delete = ts.order_delete(
            event_id=event['id'],
            order_uuid=order['order_uuid'],
            order_id=order['order_id'],
            tickets=order['tickets'],
        )

        # Заказ успешно отмечен как отменённый в сервисе продажи билетов
        if order_delete['success']:
            logger.info('Заказ {order_id} отменён в сервисе продажи билетов'.format(
                order_id=order['order_id']
                )
            )

            # Отмена заказа в БД
            order['status'] = 'cancelled'
            Order.objects.filter(id=order['order_uuid']).update(status=order['status'])

            logger.info('Статус заказа: {status}'.format(
                status=ORDER_STATUS[order['status']]['description'])
            )
        # Заказ НЕ удалось отметить как отменённый в сервисе продажи билетов
        else:
            logger.info('Заказ {order_id} НЕ удалось отменить в сервисе продажи билетов'.format(
                order_id=order['order_id']
                )
            )

        # Сообщения об ошибке для вывода на странице или в лог-файле
        messages = [
            {'level': 'error', 'message': 'К сожалению, в процессе оплаты возникла ошибка. 😞'},
            {'level': 'error', 'message': '{code} {message}'.format(
                code=payment_status['error_code'],
                message=payment_status['error_message']
            )},
            {'level': 'info',  'message': '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                event_url=event['url']
            )},
        ]

        for msg in messages:
            result['messages'].append(msg)

        return result
