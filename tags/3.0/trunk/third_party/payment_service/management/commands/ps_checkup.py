import logging
from datetime import timedelta
from mail_templated import EmailMessage

from django.core.mail.backends.smtp import EmailBackend
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F

from project.shortcuts import timezone_now

from api.views.payment import success_or_error

from bezantrakta.order.models import Order
from bezantrakta.order.order_basket import OrderBasket


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
        self.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(now))

        # Список UUID заказов с незавершёнными онлайн-оплатами
        self.stdout.write('Поиск незавершённых оплат...')
        unfinished_orders = list(Order.objects.annotate(
            order_uuid=F('id')
        ).values_list('order_uuid', flat=True).filter(payment='online', status='ordered'))

        # Если в БД есть незавершённые оплаты
        if len(unfinished_orders) > 0:
            # Получение билетов в заказе
            for order_uuid in unfinished_orders:
                basket = OrderBasket(order_uuid=order_uuid, logger='payment_service.checkup')

                # Текущее время
                now = timezone_now()
                # Дата создания онлайн-оплаты
                updated = basket.order['updated']
                # Время после создания оплаты
                now_minus_updated = now - updated
                # Таймаут на оплату в минутах
                timeout = basket.payment_service['timeout']

                # Если таймаут на оплату уже прошёл
                if now_minus_updated > timedelta(minutes=timeout):
                    self.log('\nЗаказ с незавершённой оплатой:')
                    self.log('------------------------------')
                    self.log('\nbasket.order ps_checkup start{}'.format(basket.order))
                    self.log('\nНезавершённая оплата: {}'.format(basket.order['payment_id']))
                    self.log('Таймаут на оплату: {}'.format(timeout))
                    self.log('Дата заказа: {:%Y-%m-%d %H:%M:%S}'.format(updated))
                    self.log('Текущее время: {:%Y-%m-%d %H:%M:%S}'.format(now))
                    self.log('Разница во времени: {}'.format(now_minus_updated))

                    self.log('\nПроверка статуса оплаты...')

                    # Проверка статуса оплаты
                    payment_status = basket.payment_status()

                    # Обработка успешной или НЕуспешной оплаты
                    result = success_or_error(basket, payment_status)

                    # Если оплата завершилась успешно
                    if result['success']:
                        self.log('\nПодтверждён заказ {order_id} с успешной онлайн-оплатой {payment_id}'.format(
                                order_id=basket.order['order_id'],
                                payment_id=basket.order['payment_id']
                            )
                        )
                    # Если оплата завершилась НЕуспешно - логирование информации об ошибке
                    else:
                        self.log('\nОтменён заказ {order_id} с НЕуспешной онлайн-оплатой {payment_id}'.format(
                                order_id=basket.order['order_id'],
                                payment_id=basket.order['payment_id']
                            )
                        )

                    basket.delete()

        # Если в БД нет незавершённых оплат
        else:
            self.log('На момент запуска нет незавершённых оплат', level='NOTICE')
