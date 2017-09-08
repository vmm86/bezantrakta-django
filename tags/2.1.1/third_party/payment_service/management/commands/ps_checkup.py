import logging
from datetime import timedelta
from mail_templated import EmailMessage

from django.core.mail.backends.smtp import EmailBackend
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F

from project.shortcuts import timezone_now

from bezantrakta.event.cache import get_or_set_cache as get_or_set_event_cache

from bezantrakta.order.models import Order, OrderTicket
from bezantrakta.order.settings import ORDER_DELIVERY, ORDER_PAYMENT, ORDER_STATUS

from third_party.payment_service.cache import get_or_set_cache as get_or_set_payment_service_cache
from third_party.payment_service.cache import payment_service_instance

from third_party.ticket_service.cache import get_or_set_cache as get_or_set_ticket_service_cache
from third_party.ticket_service.cache import ticket_service_instance


class Command(BaseCommand):
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
            'total'
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
                    order['tickets'] = list(OrderTicket.objects.filter(order_id=order['order_uuid']).values())
                except OrderTicket.DoesNotExist:
                    self.log('В заказе {order_id} нет ни одного билета!', level='ERROR'.format(
                        order_id=order['order_id'])
                    )
                    continue

                # Экземпляр класса сервиса онлайн-оплаты
                payment_service = {}
                payment_service['info'] = get_or_set_payment_service_cache(order['payment_service_id'])
                ps = payment_service_instance(order['payment_service_id'])

                # Получение таймаута на оплату в минутах
                timeout = ps.timeout

                # Дата запроса оплаты плюс таймаут на оплату
                now = timezone_now()
                now_minus_order_datetime = now - order['datetime']

                # Если таймаут на оплату уже прошёл
                if now_minus_order_datetime > timedelta(minutes=timeout):
                    self.log('\nНезавершённая оплата: {order}'.format(order=order))

                    self.log('\nТаймаут на оплату: {timeout}'.format(timeout=timeout))

                    self.log('\nДата заказа: {:%Y-%m-%d %H:%M:%S}'.format(order['datetime']))
                    self.log('Текущее время: {:%Y-%m-%d %H:%M:%S}'.format(now))
                    self.log('Разница во времени: {}'.format(now_minus_order_datetime))

                    self.log('\nПроверка статуса оплаты...')

                    # Экземпляр класса сервиса продажи билетов
                    event = {}
                    event['info'] = get_or_set_event_cache(order['event_uuid'])

                    # Получение реквизитов покупателя
                    customer = {}
                    customer['delivery'] = order['delivery']
                    customer['payment'] = order['payment']
                    customer['name'] = order['name']
                    customer['email'] = order['email']
                    customer['phone'] = order['phone']

                    # Экземпляр класса сервиса продажи билетов
                    ticket_service = {}
                    ticket_service['info'] = get_or_set_ticket_service_cache(order['ticket_service_id'])
                    ts = ticket_service_instance(order['ticket_service_id'])

                    # Проверка статуса оплаты
                    payment_status = ps.payment_status(payment_id=order['payment_id'])

                    # Если оплата прошла НЕуспешно
                    if not payment_status['success']:
                        self.log('\nОплата {payment_id} завершилась НЕуспешно'.format(
                            payment_id=order['payment_id'])
                        )

                        # Отмена заказа в сервисе продажи билетов
                        ts.order_delete(
                            event_id=order['event_id'],
                            order_uuid=order['order_uuid'],
                            order_id=order['order_id'],
                            tickets=order['tickets'],
                        )
                        self.log('Отмена заказа в сервисе продажи билетов...')

                        # Отмена заказа в БД
                        order['status'] = 'cancelled'
                        self.log('Статус заказа: {status}'.format(
                            status=ORDER_STATUS[order['status']]['description']),
                            level='NOTICE'
                        )

                        Order.objects.filter(id=order['order_uuid']).update(status=order['status'])

        # Если в БД нет незавершённых оплат
        else:
            self.log('На момент запуска нет незавершённых оплат', level='NOTICE')
