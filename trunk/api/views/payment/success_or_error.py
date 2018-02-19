from project.shortcuts import build_absolute_url


def success_or_error(basket, payment_status):
    """Обработка успешной или НЕуспешной оплаты.

    Args:
        basket (bezantrakta.order.order_basket.OrderBasket): Класс для работы с заказом.
        payment_status (dict): Статус онлайн-оплаты.

    Returns:
        dict: Словарь ``result`` с информацией об успешном или НЕуспешном завершении заказа с онлайн-оплатой.
            Содержимое результата:
                * **success** (bool): Успешное (``True``) или НЕуспешное (``False``) завершение заказа.
                * **messages** (list): Сообщения для последующего использования. В случае успешного завершения заказа - пустой список, в случае НЕуспешного завершения заказа - список из словарей с ключами ``level`` (уровень ошибки) и ``message`` (сообщение об ошибке).
    """
    # Формирование ответа
    result = {}
    result['success'] = None
    result['messages'] = []

    # Если оплата завершилась успешно
    if payment_status['success']:
        # Подтверждение оплаты в сервисе продажи билетов
        order_approve = basket.order_approve()

        basket.logger.info('\nbasket.order payment approved: {}'.format(basket.order))

        # Заказ успешно подтверждён как оплаченный в сервисе продажи билетов
        if order_approve['success']:
            result['success'] = True

            # Отправка email администратору и покупателю
            basket.email_admin()
            basket.email_customer()
        # Заказ НЕ удалось подтвердить как оплаченный в сервисе продажи билетов
        else:
            result['success'] = False

            # Сообщения для вывода на странице или в лог-файле
            messages = [
                {
                    'level': 'error',
                    'message': 'К сожалению, ваш заказ {order_id} не смог завершиться успешно. 🙁'.format(
                        order_id=basket.order['order_id']
                    )
                },
                {
                    'level': 'info',
                    'message': 'Заказ будет завершён в ближайшее время с отправкой уведомления на указанный вами email.'
                },
                {
                    'level': 'info',
                    'message': 'Если подтверждения не последует - <a href="{contacts_url}" target="_blank">свяжитесь с администратором сайта</a>.'.format(
                        contacts_url=build_absolute_url(basket.domain_slug, '/kontakty/')
                    )
                },
                {
                    'level': 'info',
                    'message': '👉 <a href="/">Перейти на главную</a>.'.format(
                        event_url=basket.event['url']
                    )
                },
            ]

            for msg in messages:
                result['messages'].append(msg)

        return result
    # Если оплата завершилась НЕуспешно
    else:
        result['success'] = False

        # Отмена заказа в сервисе продажи билетов
        basket.order_cancel()

        # Сообщения об ошибке для вывода на странице или в лог-файле
        messages = [
            {'level': 'error', 'message': 'К сожалению, в процессе оплаты возникла ошибка. 🙁'},
            {'level': 'error', 'message': '{code} {message}'.format(
                code=payment_status['code'],
                message=payment_status['message']
            )},
            {'level': 'info',  'message': '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                event_url=basket.event_url
            )},
        ]

        for msg in messages:
            result['messages'].append(msg)

        return result
