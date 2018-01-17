import logging
import simplejson as json
import uuid
from mail_templated import EmailMessage
from random import randint

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.db.utils import IntegrityError
from django.shortcuts import redirect

from project.cache import cache_factory
from project.shortcuts import message, render_messages, timezone_now

from ..models import Order, OrderTicket
from ..settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS, ORDER_TYPE


def order(request):
    """Получение контактных данных покупателя, параметров заказа и проведение заказа выбранного типа.

    Сначала собирается необходимая информация о событии, сервисе продажи билетов и онлайн-оплаты, покупателе, заказе.

    Заказы с оплатой наличными завершаются в этом же методе с отправкой уведомлений администратору и покупателю.

    Заказы с онлайн-оплатой перенаправляются на платёжную форму (URL приходит в ответе на запрос новой онлайн-оплаты).
    Они оформляются в видах ``payment_service.payment_success`` или ``payment_service.payment_error`` в зависимости от результата оплаты.
    """
    logger = logging.getLogger('bezantrakta.order')

    if request.method == 'POST':
        # Получение параметров сайта
        domain = cache_factory('domain', request.domain_slug)

        # Получение параметров события
        event_uuid = uuid.UUID(request.COOKIES.get('bezantrakta_event_uuid', None))
        event = cache_factory('event', event_uuid)
        if event is None:
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, такого события не существует. 🙁'),
                message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
            ]
            render_messages(request, msgs)
            return redirect('error')
        event['id'] = event['ticket_service_event']

        # Настройки сервиса продажи билетов
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        # Экземпляр класса сервиса продажи билетов
        ts = ticket_service['instance']

        # Настройки сервиса онлайн-оплаты
        payment_service = cache_factory(
            'payment_service', event['payment_service_id'],
            domain_slug=domain['domain_slug']
        )
        # Экземпляр сервиса онлайн-оплаты (с указанием URL завершения удачной или НЕудачной оплаты)
        ps = payment_service['instance']

        # Получение реквизитов покупателя
        customer = {}
        customer['order_type'] = request.POST.get('customer_order_type')
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
                message('error', 'При оформлении получен неправильный уникальный номер заказа! 🙁'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['url'])
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')
        else:
            order['tickets'] = json.loads(request.COOKIES.get('bezantrakta_order_tickets', []))
            order['count'] = int(request.COOKIES.get('bezantrakta_order_count', 0))
            order['total'] = ps.decimal_price(request.COOKIES.get('bezantrakta_order_total', 0))

            # Типы заказа билетов
            order['type'] = customer['order_type']

            # Процент сервисного сбора
            order['extra'] = event['settings']['extra'][order['type']]

            # Получение общей суммы заказа в зависимости от возможных наценок/скидок

            # Для любого типа заказа - с учётом сервисного сбора для каждого билета в заказе (если он задан)
            order['overall'] = ps.total_plus_extra(order['tickets'], order['total'], order['extra'])

            # При доставке курьером - с учётом стоимости доставки курьером (если она задана)
            if customer['delivery'] == 'courier':
                # Стоимость доставки курьером
                order['courier_price'] = ps.decimal_price(ticket_service['settings']['courier_price'])
                # Общая сумма заказа (с учётом сервисного сбора и стоимости доставки курьером)
                order['overall'] = (
                    ps.total_plus_courier_price(order['overall'], order['courier_price']) if
                    order['extra'] > 0 else
                    ps.total_plus_courier_price(order['total'], order['courier_price'])
                )

            # При онлайн-оплате - с учётом комиссии сервиса онлайн-оплаты (если она задана)
            if customer['payment'] == 'online':
                # Процент комиссии сервиса онлайн-оплаты
                order['commission'] = ps.decimal_price(payment_service['settings']['init']['commission'])
                # Общая сумма заказа (с учётом сервисного сбора и комиссии сервиса онлайн-оплаты)
                order['overall'] = (
                    ps.total_plus_commission(order['overall']) if
                    order['extra'] > 0 else
                    ps.total_plus_commission(order['total'])
                )

            # Логирование базовой информации о заказе
            now = timezone_now()
            logger.info('\n----------Обработка заказа {order_uuid}----------'.format(order_uuid=order['order_uuid']))
            logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

            logger.info('Сайт: {title} ({id})'.format(title=domain['domain_title'], id=domain['domain_id']))
            logger.info('Сервис продажи билетов: {title} ({id})'.format(
                    title=ticket_service['title'],
                    id=ticket_service['id']
                )
            )

            logger.info('UUID события: {event_uuid}'.format(event_uuid=event['event_uuid']))
            logger.info('Идентификатор события: {event_id}'.format(event_id=event['id']))

            logger.info('\nСобытие')
            logger.info(event)

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
            logger.info('Сумма цен на билеты: {total}'.format(total=order['total']))
            logger.info('Общая сумма заказа: {total}'.format(total=order['overall']))

            # Проверка состояния билетов в предварительном резерве (если такой функционал предусмотрен)
            logger.info('\nПроверка состояния билетов в предварительном резерве...')
            for ticket in order['tickets']:
                ticket['event_id'] = event['id']
                ticket_status = ts.ticket_status(**ticket)

                if not ticket_status['success']:
                    # Сообщение об ошибке
                    msgs = [
                        message('error', 'К сожалению, произошла ошибка резерва билетов. 🙁'),
                        message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                                event_url=event['url'])
                                ),
                    ]
                    render_messages(request, msgs)
                    return redirect('error')

                ticket['status'] = ticket_status['status']
                logger.info('🎫 {ticket_status}'.format(ticket_status=str(ticket_status)))
            order['tickets'][:] = [t for t in order['tickets'] if t.get('status') in ('reserved', 'bypass',)]

            if len(order['tickets']) == 0:
                logger.error('Резерв на все места в заказе истёк!')

                # Сообщение об ошибке
                msgs = [
                    message('error', 'К сожалению, резерв на все места в заказе истёк. 🙁'),
                    message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                            event_url=event['url'])
                            ),
                ]
                render_messages(request, msgs)
                return redirect('error')

            # Создание нового заказа из билетов в предварительном резерве
            logger.info('\nСоздание заказа...')
            order_create = ts.order_create(
                event_id=event['id'],
                order_uuid=order['order_uuid'],
                customer=customer,
                tickets=order['tickets']
            )
            logger.info('order[tickets]: {}'.format(order['tickets']))
            logger.info('order_create: {}'.format(order_create))

            # Если заказ успешно создан - получение идентификатора заказа и штрих-кодов
            if order_create['success']:
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
                            if settings.DEBUG:
                                logger.info('\n{o_uuid} == {t_uuid}: {cond}'.format(
                                    o_uuid=uuid.UUID(o['ticket_uuid']),
                                    t_uuid=uuid.UUID(t['ticket_uuid']),
                                    cond=uuid.UUID(o['ticket_uuid']) == uuid.UUID(t['ticket_uuid']))
                                )
                            t['bar_code'] = (
                                o['bar_code'] if
                                'bar_code' in o and o['bar_code'] is not None else
                                ''.join([str(randint(0, 9)) for x in range(ts.bar_code_length)])
                            )
                            logger.info('t[bar_code]: {barcode}'.format(barcode=t['bar_code']))
                        else:
                            continue

                # Проверка состояния билетов в созданном заказе (если такой функционал предусмотрен)
                logger.info('\nПроверка состояния билетов в созданном заказе')
                for ticket in order['tickets']:
                    ticket_status = ts.ticket_status(**ticket)
                    ticket['status'] = ticket_status['status']
                    logger.info('* {ticket_status}'.format(ticket_status=str(ticket_status)))
                order['tickets'][:] = [t for t in order['tickets'] if t.get('status') in ('ordered', 'bypass',)]

                now = timezone_now()
                # Сохранение предварительного заказа
                try:
                    Order.objects.create(
                        id=order['order_uuid'],
                        ticket_service_id=ticket_service['id'],
                        ticket_service_order=order['order_id'],
                        event_id=event['event_uuid'],
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
                        total=order['overall'],
                        domain_id=domain['domain_id']
                    )
                except IntegrityError:
                    logger.critical('Такой заказ уже был добавлен в базу данных ранее!')

                    # Сообщение об ошибке
                    msgs = [
                        message('warning', 'Такой заказ уже был создан ранее! 🙁'),
                        message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                                event_url=event['url'])
                                ),
                    ]
                    render_messages(request, msgs)
                    return redirect('error')
                else:
                    logger.info('\nЗаказ {order_uuid} сохранён в БД'.format(order_uuid=order['order_uuid']))

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
                                domain_id=domain['domain_id']
                            )
                        except IntegrityError:
                            logger.critical('Невозможно добавить билет в БД!')
                        else:
                            logger.info('Билет {} сохранён в БД'.format(t['ticket_uuid']))

                    # Если оплата наличными - заказ завершается
                    if customer['payment'] == 'cash':
                        # Подтверждение обычного резерва в БД
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
                        admin_email.send()
                        logger.info('Email-уведомление администратору отправлено')
                        customer_email.send()
                        logger.info('Email-уведомление покупателю отправлено')

                        return redirect('order:confirmation', order_uuid=order['order_uuid'])
                    # Если онлайн-оплата - запрос новой оплаты
                    elif customer['payment'] == 'online':
                        # Создание новой онлайн-оплаты
                        payment_create = ps.payment_create(
                            event_uuid=event['event_uuid'],
                            event_id=event['id'],
                            customer=customer,
                            order=order
                        )

                        logger.info('Создание онлайн-оплаты: {payment_create}'.format(payment_create=payment_create))

                        # Если запрос на оплату успешный
                        if payment_create['success']:
                            logger.info('\nСоздание новой онлайн-оплаты завершилось успешно')

                            # Получение номера оплаты
                            payment_id = payment_create['payment_id']
                            payment_url = payment_create['payment_url']

                            now = timezone_now()
                            # Сохранение идентификатора оплаты в БД
                            Order.objects.filter(id=order['order_uuid']).update(
                                datetime=now,
                                payment_id=payment_id
                            )
                            logger.info('Идентификатор оплаты: {payment_id}'.format(payment_id=payment_id))
                            logger.info('Перенаправление на URL платёжной формы...')

                            # Редирект на URL платёжной формы
                            return redirect(payment_url)
                        # Если запрос на оплату НЕуспешный
                        else:
                            logger.info('\nСоздание новой онлайн-оплаты завершилось НЕуспешно')

                            # Отмена заказа в сервисе продажи билетов
                            order_cancel = ts.order_cancel(
                                event_id=event['id'],
                                order_uuid=order['order_uuid'],
                                order_id=order['order_id'],
                                tickets=order['tickets'],
                            )

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
                                    status=ORDER_STATUS[order['status']]['description'])
                                )
                            # Заказ НЕ удалось отметить как отменённый в сервисе продажи билетов
                            else:
                                logger.info('Заказ {order_id} НЕ удалось отменить в сервисе продажи билетов'.format(
                                    order_id=order['order_id']
                                    )
                                )

                            # Сообщение об ошибке
                            msgs = [
                                message('error', 'К сожалению, запрос оплаты завершился с ошибкой. 🙁'),
                                message(
                                    'error',
                                    '{code} {message}'.format(
                                        code=payment_create['code'],
                                        message=payment_create['message'])
                                ),
                                message(
                                    'info',
                                    '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                                        event_url=event['url'])
                                ),
                            ]
                            render_messages(request, msgs)
                            return redirect('error')
            # Если заказ НЕ создан успешно
            else:
                logger.critical('Ошибка при создании заказа!')

                # Освобождение предварительного резерва
                for ticket in order['tickets']:
                    ticket['action'] = 'remove'
                    ticket['order_uuid'] = order['order_uuid']
                    ticket['event_id'] = event['id']
                    remove = ts.reserve(**ticket)

                    if remove['success']:
                        logger.critical(
                            'Удалён предварительный резерв: {sector} {sector_id} {row_id} {seat_id}'.format(
                                sector=ticket['sector_title'],
                                sector_id=ticket['sector_id'],
                                row_id=ticket['row_id'],
                                seat_id=ticket['seat_id'])
                        )
                    else:
                        logger.critical(
                            'Не удалось удалить предварительный резерв: {sector} {sector_id} {row_id} {seat_id}'.format(
                                sector=ticket['sector_title'],
                                sector_id=ticket['sector_id'],
                                row_id=ticket['row_id'],
                                seat_id=ticket['seat_id'])
                        )

                # Сообщение об ошибке
                msgs = [
                    message('error', 'Ошибка при создании заказа! 🙁'),
                    message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=event['url'])
                    ),
                ]
                render_messages(request, msgs)
                return redirect('error')

    # Если это не POST-запрос при оформлении заказа - редирект на главную страницу
    return redirect('/')
