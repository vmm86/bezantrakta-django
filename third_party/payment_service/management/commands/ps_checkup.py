import logging
from datetime import timedelta
from mail_templated import EmailMessage

from django.core.mail.backends.smtp import EmailBackend
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.settings import ORDER_DELIVERY_CAPTION, ORDER_PAYMENT_CAPTION, ORDER_STATUS_CAPTION
from bezantrakta.order.shortcuts import success_or_error


class Command(BaseCommand):
    """Поиск незавершённых оплат в сервисах онлайн-оплаты.

    Если таймаут на конкретную оплату уже прошёл - проверяется статус оплаты.

    Если оплата завершилась НЕуспешно - отменятся заказ в сервисе продажи билетов.

    Задание должно запускаться в cron с определённой периодичностью:
    ``***** source {venv/biv/activate} && python {корень проекта}/manage.py ps_checkup``
    """
    help = """
Поиск незавершённых оплат в сервисах онлайн-оплаты.___________________________
Если таймаут на конкретную оплату уже прошёл - проверяется статус оплаты._____
Если оплата завершилась НЕуспешно - отменятся заказ в сервисе продажи билетов.
______________________________________________________________________________
Задание должно запускаться в cron с определённой периодичностью:______________
***** source {venv/biv/activate} && python {корень проекта}/manage.py command
    """
    logger = logging.getLogger('payment_service.checkup')

    def log(self, msg, level=None):
        if level is None:
            self.stdout.write(msg)
            self.logger.info(msg)
        else:
            if level == 'INFO':
                self.stdout.write(self.style.WARNING(msg))
                self.logger.info('[INFO] {}'.format(msg))
            elif level == 'SUCCESS':
                self.stdout.write(self.style.SUCCESS(msg))
                self.logger.info('[SUCCESS] {}'.format(msg))
            elif level == 'NOTICE':
                self.stdout.write(self.style.NOTICE(msg))
                self.logger.error('[NOTICE] {}'.format(msg))
            elif level == 'ERROR':
                self.stdout.write(self.style.ERROR(msg))
                self.logger.critical('[ERROR] {}'.format(msg))

    def handle(self, *args, **options):
        now = timezone_now()
        self.logger.info('\n--------------------------------------------------')
        self.logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))

        self.stdout.write('Поиск незавершённых оплат...')
        unfinished_orders = list(Order.objects.annotate(
            event_uuid=F('event'),
            event_id=F('ticket_service_event'),
            order_uuid=F('id'),
            order_id=F('ticket_service_order'),
            payment_service_id=F('ticket_service__payment_service_id'),
            domain_slug=F('domain__slug'),
            overall=F('total'),
        ).values(
            'event_uuid',
            'event_id',
            'order_uuid',
            'order_id',
            'ticket_service_id',
            'payment_service_id',
            'datetime',
            'name',
            'email',
            'phone',
            'delivery',
            'payment',
            'payment_id',
            'status',
            'tickets_count',
            'total',
            'overall',
            'domain_slug'
        ).filter(
            payment='online',
            status='ordered',
            # datetime__gt=Value(F('datetime') - timedelta(minutes=5))
        ))

        # Если в БД есть незавершённые оплаты
        if len(unfinished_orders) > 0:

            # Получение билетов в заказе
            for order in unfinished_orders:
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
                        # 'price_group_id',
                        'price'
                    ).filter(
                        order_id=order['order_uuid']
                    ))
                except OrderTicket.DoesNotExist:
                    self.log('В заказе {order_id} нет ни одного билета!', level='ERROR'.format(
                        order_id=order['order_id'])
                    )
                    continue

                # Получение параметров сайта
                domain = cache_factory('domain', order['domain_slug'])

                # Экземпляр класса сервиса онлайн-оплаты
                payment_service = cache_factory('payment_service', order['payment_service_id'])
                ps = payment_service['instance']

                # Получение таймаута на оплату в минутах
                timeout = ps.timeout

                # Дата запроса оплаты плюс таймаут на оплату
                now = timezone_now()
                now_minus_order_datetime = now - order['datetime']

                # Если таймаут на оплату уже прошёл
                if now_minus_order_datetime > timedelta(minutes=timeout):
                    self.log('\nЗаказ с незавершённой оплатой:')
                    self.log('------------------------------')
                    self.log('{}'.format(order))
                    self.log('\nНезавершённая оплата: {order}'.format(order=order))
                    self.log('Таймаут на оплату: {timeout}'.format(timeout=timeout))
                    self.log('Дата заказа: {:%Y-%m-%d %H:%M:%S}'.format(order['datetime']))
                    self.log('Текущее время: {:%Y-%m-%d %H:%M:%S}'.format(now))
                    self.log('Разница во времени: {}'.format(now_minus_order_datetime))

                    self.log('\nПроверка статуса оплаты...')

                    # Информация о событии из кэша
                    event = cache_factory('event', order['event_uuid'])
                    event['id'] = event['ticket_service_event']

                    # Получение реквизитов покупателя
                    customer = {}
                    customer['delivery'] = order['delivery']
                    customer['payment'] = order['payment']
                    customer['name'] = order['name']
                    customer['email'] = order['email']
                    customer['phone'] = order['phone']

                    # Проверка статуса оплаты
                    payment_status = ps.payment_status(payment_id=order['payment_id'])
                    self.log('\nСтатус оплаты: {payment_status}'.format(payment_status=payment_status))

                    # Обработка успешной или НЕуспешной оплаты
                    result = success_or_error(domain, event, order, payment_status, self.logger)

                    # Если оплата завершилась успешно
                    if result['success']:
                        self.log('\nПодтверждён заказ {order_id} с успешной онлайн-оплатой {payment_id}'.format(
                                order_id=order['order_id'],
                                payment_id=order['payment_id']
                            )
                        )
                    # Если оплата завершилась НЕуспешно - логирование информации об ошибке
                    else:
                        self.log('\nОтменён заказ {order_id} с НЕуспешной онлайн-оплатой {payment_id}'.format(
                                order_id=order['order_id'],
                                payment_id=order['payment_id']
                            )
                        )

        # Если в БД нет незавершённых оплат
        else:
            self.log('На момент запуска нет незавершённых оплат', level='NOTICE')
