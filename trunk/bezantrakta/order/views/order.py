import logging
import simplejson as json
import uuid
from mail_templated import EmailMessage
from random import randint

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.db.utils import IntegrityError
from django.shortcuts import redirect

from project.shortcuts import message, render_messages, timezone_now

from bezantrakta.event.cache import get_or_set_cache as get_or_set_event_cache
from bezantrakta.event.shortcuts import add_small_vertical_poster

from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS

from third_party.payment_service.cache import get_or_set_cache as get_or_set_payment_service_cache
from third_party.payment_service.cache import payment_service_instance

from third_party.ticket_service.cache import get_or_set_cache as get_or_set_ticket_service_cache
from third_party.ticket_service.cache import ticket_service_instance


def order(request):
    """Получение контактных данных покупателя, параметров заказа и проведение заказа выбранного типа.

    Сначала собирается вся необдимая информация о событии, сервисе продажи билетов и онлайн-оплаты, покупателе, заказе.

    Заказы с оплатой наличными завершаются в этом же методе с отправкой уведомлений администратору и покупателю.

    Заказы с онлайн-оплатой редиректятся на форму оплаты (её адрес приходит в ответе на запрос новой онлайн-оплаты).
    Они оформляются в видах payment_success или payment_error в зависимости от результата оплаты.
    """
    logger = logging.getLogger('bezantrakta.order')

    if request.method == 'POST':
        # Получение параметров события
        event = {}
        event['uuid'] = uuid.UUID(request.COOKIES.get('bezantrakta_event_uuid', None))
        event['info'] = get_or_set_event_cache(event['uuid'])
        event['id'] = event['info']['ticket_service_event']
        # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
        add_small_vertical_poster(request, event['info'])

        # Экземпляр класса сервиса продажи билетов
        ticket_service = {}
        ticket_service['id'] = event['info']['ticket_service_id']
        ticket_service['info'] = get_or_set_ticket_service_cache(ticket_service['id'])

        ts = ticket_service_instance(ticket_service['id'])

        # Экземпляр сервиса онлайн-оплаты (с указанием URL завершения удачной или НЕудачной оплаты)
        payment_service = {}
        payment_service['id'] = event['info']['payment_service_id']
        payment_service['info'] = get_or_set_payment_service_cache(payment_service['id'])

        ps = payment_service_instance(payment_service['id'], url_domain=request.url_domain)

        # Получение реквизитов покупателя
        customer = {}
        # customer['order_type'] = request.POST.get('customer_order_type')
        customer['delivery'] = request.POST.get('customer_delivery')
        customer['payment'] = request.POST.get('customer_payment')
        customer['name'] = request.POST.get('customer_name')
        customer['email'] = request.POST.get('customer_email')
        customer['phone'] = request.POST.get('customer_phone')
        customer['is_courier'] = True if customer['delivery'] == 'courier' else False
        customer['address'] = request.POST.get('customer_address') if customer['delivery'] == 'courier' else None

        # Получение параметров заказа
        order = {}
        try:
            order['order_uuid'] = uuid.UUID(request.COOKIES.get('bezantrakta_order_uuid', None))
        except (AttributeError, TypeError, ValueError) as e:
            logger.critical('Неправильный уникальный номер заказа!')
            logger.critical(e)

            # Сообщение об ошибке
            msgs = [
                message('error', 'При оформлении получен неправильный уникальный номер заказа! 😞'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['info']['url'])
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')
        else:
            order['tickets'] = json.loads(request.COOKIES.get('bezantrakta_order_tickets', []))
            order['count'] = int(request.COOKIES.get('bezantrakta_order_count', 0))
            order['total'] = ts.decimal_price(request.COOKIES.get('bezantrakta_order_total', 0))

            # При доставке курьером - общая сумма заказа плюс стоимость доставки курьером
            if customer['delivery'] == 'courier':
                order['total'] += ps.decimal_price(ticket_service['info']['settings']['courier_price'])
            # При онлайн-оплате - общая сумма заказа с комиссией сервиса онлайн-оплаты
            if customer['payment'] == 'online':
                order['total'] = ps.total_plus_commission(order['total'])

            # Получение параметров сайта
            domain = {}
            domain['id'] = request.domain_id
            domain['title'] = request.domain_title
            domain['slug'] = request.domain_slug
            domain['url'] = request.url_domain
            domain['settings'] = request.domain_settings

            # Логирование базовой информации о заказе
            now = timezone_now()
            logger.info('\n----------Обработка заказа {order_uuid}----------'.format(order_uuid=order['order_uuid']))
            logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

            logger.info('Сайт: {title} ({id})'.format(title=domain['title'], id=domain['id']))
            logger.info('Сервис продажи билетов: {title} ({id})'.format(
                    title=ticket_service['info']['title'],
                    id=ticket_service['id']
                )
            )

            logger.info('UUID события: {event_uuid}'.format(event_uuid=event['uuid']))
            logger.info('Идентификатор события: {event_id}'.format(event_id=event['id']))

            logger.info('\nСобытие')
            logger.info(event['info'])

            logger.info('\nРеквизиты покупателя')
            logger.info('Получение билетов: {delivery}'.format(delivery=ORDER_DELIVERY[customer['delivery']]))
            if customer['delivery'] == 'courier':
                logger.info('Адрес доставки: {address}'.format(address=customer['address']))
            logger.info('Оплата: {payment}'.format(payment=ORDER_PAYMENT[customer['payment']]))
            logger.info('ФИО: {name}'.format(name=customer['name']))
            logger.info('Email: {email}'.format(email=customer['email']))
            logger.info('Телефон: {phone}'.format(phone=customer['phone']))

            logger.info('\nПараметры заказа')
            logger.info('UUID заказа: {order_uuid}'.format(order_uuid=order['order_uuid']))
            logger.info('Билеты в заказе:')
            for ticket in order['tickets']:
                logger.info('* {ticket}'.format(ticket=ticket))
            logger.info('Число билетов: {count}'.format(count=order['count']))
            logger.info('Сумма заказа: {total}'.format(total=order['total']))

            # Проверка состояния билетов в предварительной брони
            logger.info('\nПроверка состояния билетов в предварительной брони...')
            for ticket in order['tickets']:
                ticket['event_id'] = event['id']
                ticket_status = ts.ticket_status(**ticket)
                ticket['seat_status'] = ticket_status['seat_status']
                logger.info('* {ticket_status}'.format(ticket_status=str(ticket_status)))
            order['tickets'][:] = [t for t in order['tickets'] if t.get('seat_status') == 'reserved']

            if len(order['tickets']) == 0:
                logger.error('Бронь на все места в заказе истекла - заказ отменён!')

                # Сообщение об ошибке
                msgs = [
                    message('error', 'Бронь на все места в заказе истекла - заказ отменён! 😞'),
                    message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                            event_url=event['info']['url'])
                            ),
                ]
                render_messages(request, msgs)
                return redirect('error')

            # Создание нового заказа из предварительной брони
            logger.info('\nСоздание заказа...')
            order_create = ts.order_create(
                event_id=event['id'],
                order_uuid=order['order_uuid'],
                customer=customer,
                tickets=order['tickets']
            )
            logger.info('order[tickets]: {}'.format(order['tickets']))
            logger.info('order_create: {}'.format(order_create))

            # Если заказ успешен - получение идентификатора заказа и штрих-кодов
            if 'order_id' in order_create and 'tickets' in order_create:
                order['status'] = 'ordered'
                logger.info('Статус заказа: {status}'.format(
                    status=ORDER_STATUS[order['status']]['description'])
                )
                order['order_id'] = order_create['order_id']
                logger.info('Идентификатор заказа: {order_id}'.format(order_id=order['order_id']))

                # Получение штрих-кодов для билетов в заказе из ответа сервиса продажи билетов
                # Если по каким-то причинам штрих-код не получен - он генерируется автоматически
                for o in order_create['tickets']:
                    for t in order['tickets']:
                        if uuid.UUID(o['ticket_uuid']) == uuid.UUID(t['ticket_uuid']):
                            logger.info('\n{o_uuid} == {t_uuid}: {cond}'.format(
                                o_uuid=uuid.UUID(o['ticket_uuid']),
                                t_uuid=uuid.UUID(t['ticket_uuid']),
                                cond=uuid.UUID(o['ticket_uuid']) == uuid.UUID(t['ticket_uuid']))
                            )
                            t['bar_code'] = (
                                o['bar_code'] if
                                'bar_code' in o and o['bar_code'] is not None else
                                ''.join([str(randint(0, 9)) for x in range(20)])
                            )
                            logger.info('t[bar_code]: ', t['bar_code'])
                        else:
                            continue

                # Проверка состояния билетов в созданном заказе
                logger.info('\nПроверка состояния билетов в созданном заказе')
                for ticket in order['tickets']:
                    ticket_status = ts.ticket_status(**ticket)
                    ticket['seat_status'] = ticket_status['seat_status']
                    logger.info('* {ticket_status}'.format(ticket_status=str(ticket_status)))
                order['tickets'][:] = [t for t in order['tickets'] if t.get('seat_status') == 'ordered']

                now = timezone_now()
                # logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))
                # Сохранение предварительного заказа
                try:
                    Order.objects.create(
                        id=order['order_uuid'],
                        ticket_service_id=ticket_service['id'],
                        ticket_service_order=order['order_id'],
                        event_id=event['uuid'],
                        ticket_service_event=event['id'],
                        datetime=now,
                        name=customer['name'],
                        email=customer['email'],
                        phone=customer['phone'],
                        address=customer['address'],
                        delivery=customer['delivery'],
                        payment=customer['payment'],
                        payment_id=None,
                        status=order['status'],
                        tickets_count=order['count'],
                        total=order['total'],
                        domain_id=request.domain_id
                    )
                except IntegrityError:
                    logger.critical('Такой заказ уже был добавлен в базу данных ранее!')

                    # Сообщение об ошибке
                    msgs = [
                        message('warning', 'Такой заказ уже был создан ранее! 😞'),
                        message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                                event_url=event['info']['url'])
                                ),
                    ]
                    render_messages(request, msgs)
                    return redirect('error')
                else:
                    logger.info('Заказ {order_uuid} сохранён в БД'.format(order_uuid=order['order_uuid']))

                    for t in order['tickets']:
                        try:
                            OrderTicket.objects.create(
                                id=t['ticket_uuid'],
                                order_id=order['order_uuid'],
                                ticket_service_id=ticket_service['id'],
                                ticket_service_order=order['order_id'],
                                is_punched=False,
                                bar_code=t['bar_code'],
                                sector_id=t['sector_id'],
                                sector_title=t['sector_title'],
                                row_id=t['row_id'],
                                seat_id=t['seat_id'],
                                seat_title=t['seat_title'],
                                price_group_id=t['price_group_id'],
                                price=t['price'],
                                domain_id=request.domain_id
                            )
                        except IntegrityError:
                            logger.critical('Невозможно добавить билет в БД!')
                        else:
                            logger.info('Билет {} сохранён в БД'.format(t['ticket_uuid']))

                    # Если оплата наличными - заказ завершается
                    if customer['payment'] == 'cash':
                        # Подтверждение обычной брони в БД
                        order['status'] = 'approved'
                        logger.info('Статус заказа: {status}'.format(
                            status=ORDER_STATUS[order['status']]['description'])
                        )

                        Order.objects.filter(id=order['order_uuid']).update(status=order['status'])

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
                        admin_email.send()
                        logger.info('Email-уведомление администратору отправлено')
                        customer_email.send()
                        logger.info('Email-уведомление покупателю отправлено')

                        return redirect('order:confirmation', order_uuid=order['order_uuid'])
                    # Если онлайн-оплата - запрос новой оплаты и редирект на URL платёжной формы
                    elif customer['payment'] == 'online':
                        # Создание новой онлайн-оплаты
                        payment_create = ps.payment_create(
                            event_uuid=event['uuid'],
                            customer=customer,
                            order=order
                        )

                        # Успешный или НЕуспешный запрос на оплату
                        if payment_create['success']:
                            # Получение номера оплаты
                            payment_id = payment_create['payment_id']
                            payment_url = payment_create['payment_url']

                            now = timezone_now()
                            # logger.info('{:%Y-%m-%d %H:%M:%S}'.format((now)))
                            # Сохранение идентификатора оплаты в БД
                            Order.objects.filter(id=order['order_uuid']).update(
                                datetime=now,
                                payment_id=payment_id
                            )
                            logger.info('\nИдентификатор оплаты: {payment_id}'.format(payment_id=payment_id))

                            # Редирект на форму онлайн-оплаты
                            return redirect(payment_url)
                        else:
                            # Отмена заказа в БД
                            order['status'] = 'cancelled'
                            logger.info('Статус заказа: {status}'.format(
                                status=ORDER_STATUS[order['status']]['description'])
                            )

                            Order.objects.filter(id=order['order_uuid']).update(status=order['status'])

                            # Сообщение об ошибке
                            msgs = [
                                message('error', 'К сожалению, запрос оплаты завершился с ошибкой. 😞'),
                                message(
                                    'error',
                                    '{code} {message}'.format(
                                        code=payment_create['code'],
                                        message=payment_create['message'])
                                ),
                                message(
                                    'info',
                                    '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                                        event_url=event['info']['url'])
                                ),
                            ]
                            render_messages(request, msgs)
                            return redirect('error')
            # Если заказ НЕуспешен
            else:
                logger.critical('Ошибка при создании заказа!')

                # Освобождение предварительной брони
                for ticket in order['tickets']:
                    ticket['action'] = 'remove'
                    ticket['order_uuid'] = order['order_uuid']
                    ticket['event_id'] = event['id']
                    remove = ts.reserve(**ticket)

                    if remove['success']:
                        logger.critical(
                            'Снята предварительная бронь: {sector} {sector_id} {row_id} {seat_id}'.format(
                                sector=ticket['sector_title'],
                                sector_id=ticket['sector_id'],
                                row_id=ticket['row_id'],
                                seat_id=ticket['seat_id'])
                        )
                    else:
                        logger.critical(
                            'Не удалось снять предварительную бронь: {sector} {sector_id} {row_id} {seat_id}'.format(
                                sector=ticket['sector_title'],
                                sector_id=ticket['sector_id'],
                                row_id=ticket['row_id'],
                                seat_id=ticket['seat_id'])
                        )

                # Сообщение об ошибке
                msgs = [
                    message('error', 'Ошибка при создании заказа! 😞'),
                    message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['info']['url'])
                    ),
                ]
                render_messages(request, msgs)
                return redirect('error')

    # Если это не POST-запрос при оформлении заказа - редирект на главную страницу
    return redirect('/')
