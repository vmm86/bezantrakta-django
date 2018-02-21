import uuid

from django.shortcuts import redirect

from project.shortcuts import message, render_messages, timezone_now

from bezantrakta.order.order_basket import OrderBasket


def processing(request):
    """Получение параметров заказа, контактных данных покупателя и оформление заказа выбранного типа.

    Заказы с оплатой наличными завершаются в этом же методе с отправкой уведомлений администратору и покупателю.

    Заказы с онлайн-оплатой перенаправляются на платёжную форму (URL приходит в ответе на запрос новой онлайн-оплаты).
    Они оформляются в видах ``api.payment__success`` или ``api.payment__error`` в зависимости от результата оплаты.
    """
    if request.method == 'POST':
        # UUID предварительного резерва
        order_uuid = request.POST.get('order_uuid', None)
        try:
            order_uuid = uuid.UUID(order_uuid)
        except (TypeError, ValueError):
            # Сообщение об ошибке
            msgs = [
                message('error', 'Предварительный резерв некорректен или отсутствует. 🙁'),
                message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
            ]
            render_messages(request, msgs)
            return redirect('error')

        # Получение параметров предварительного резерва
        basket = OrderBasket(order_uuid=order_uuid, logger='bezantrakta.order')
        if not basket or not basket.order:
            # Сообщение об ошибке
            msgs = [
                message('error', 'Предварительный резерв некорректен или отсутствует. 🙁'),
                message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
            ]
            render_messages(request, msgs)
            return redirect('error')

        # Обход возможного отсутствия реквизитов покупателя в предварительном резерве
        empty_customer = (
            not basket.order['customer']['name'] or
            not basket.order['customer']['email'] or
            not basket.order['customer']['phone']
        )

        if empty_customer:
            if not basket.order['customer']['name']:
                basket.order['customer']['name'] = request.POST.get('customer_name', 'Фамилия Имя Отчество')
            if not basket.order['customer']['email']:
                basket.order['customer']['email'] = request.POST.get('customer_email', 'primer@mail.ru')
            if not basket.order['customer']['phone']:
                basket.order['customer']['phone'] = request.POST.get('customer_phone', '81234567890')

            basket.update()

            basket.logger.info('\ncustomer: {}'.format(basket.order['customer']))

        # Логирование базовой информации о заказе
        basket.logger.info('\n----------Обработка заказа {}----------'.format(basket.order['order_uuid']))
        basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

        basket.log()

        basket.logger.info('\nbasket.order start: {}'.format(basket.order))

        # Проверка состояния билетов в предварительном резерве
        basket.tickets_check('reserved')

        if basket.order['tickets_count'] == 0:
            basket.error('Резерв на все билеты истёк!')

            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, резерв на все места в заказе истёк. 🙁'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=basket.event_url)
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')

        # Создание нового заказа с получением штрих-кодов для каждого из успешно заказанных билетов
        order_create = basket.order_create()

        # Если заказ успешно создан - получение идентификатора заказа и штрих-кодов
        if order_create['success']:
            # Проверка состояния билетов в созданном заказе
            basket.tickets_check('ordered')

            # Получение штрих-кодов для билетов в заказе
            basket.tickets_barcode(order_create)

            basket.logger.info('\nbasket.order create: {}'.format(basket.order))

            # Сохранение созданного зааза и билетов в БД
            order_create_db = basket.order_create_db()

            if not order_create_db['success']:
                # Сообщение об ошибке
                msgs = [
                    message('warning', 'Такой заказ уже был создан ранее! 🙁'),
                    message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                            event_url=basket.event_url)
                            ),
                ]
                render_messages(request, msgs)
                return redirect('error')

            # Если оффлайн-оплата - заказ завершается
            if basket.order['payment'] == 'cash':
                # Подтверждение оплаты заказа в БД
                basket.order_status_db('approved')

                basket.logger.info('\nbasket.order approved: {}'.format(basket.order))

                # Отправка email администратору и покупателю
                basket.email_admin()
                basket.email_customer()

                return redirect('order:order_step_3', order_uuid=order_uuid)
            # Если онлайн-оплата - запрос новой оплаты
            elif basket.order['payment'] == 'online':
                # Создание новой онлайн-оплаты
                payment_create = basket.payment_create()

                # Успешный запрос на оплату
                if payment_create['success']:
                    basket.payment_create_db(payment_create)

                    basket.logger.info('Перенаправление на URL платёжной формы...')
                    return redirect(basket.payment_url)
                # НЕуспешный запрос на оплату
                else:
                    # Отмена и удаление заказа
                    order_cancel = basket.order_cancel()

                    # Заказ успешно отмечен как отменённый в сервисе продажи билетов
                    if order_cancel['success']:
                        basket.order_status_db('cancelled')

                    # Сообщение об ошибке
                    msgs = [
                        message('error', 'К сожалению, запрос оплаты завершился с ошибкой. 🙁'),
                        message(
                            'error',
                            '{code} {message}'.format(code=payment_create['code'], message=payment_create['message'])
                        ),
                        message(
                            'info',
                            '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                                event_url=basket.event_url)
                        ),
                    ]
                    render_messages(request, msgs)
                    return redirect('error')
        # Если заказ НЕ создан успешно
        else:
            basket.logger.critical('Ошибка при создании заказа!')

            # Освобождение билетов и удаление предварительного резерва
            basket.tickets_clear()

            # Сообщение об ошибке
            msgs = [
                message('error', 'Ошибка при создании заказа! 🙁'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                    event_url=basket.event_url)
                ),
            ]
            render_messages(request, msgs)
            return redirect('error')

    # Если это не POST-запрос при оформлении заказа - редирект на главную страницу
    return redirect('/')
