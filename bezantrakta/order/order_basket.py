import logging
import pytz
import uuid
from collections import OrderedDict
from decimal import Decimal
from mail_templated import EmailMessage
from operator import itemgetter
from random import randint
from smtplib import SMTPException
from time import sleep

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.db.utils import IntegrityError

from bezantrakta.order.models import Order, OrderTicket

from project.cache import cache_factory
from project.shortcuts import timezone_now

from bezantrakta.eticket.shortcuts import render_eticket


class OrderBasket():
    """Класс для работы с предварительными резервами и созданными заказами.

    Проводит определённые операции с заказом, получая информацию о нём из кэша.

    Class attributes:
        ORDER_TYPE (tuple): Типы заказа билетов (комбинация способа получения билетов и способа оплаты). Упорядочены в порядке предпочтения для показа на шаге 2 заказа билетов.
        ORDER_TYPE_MAPPING (dict): Способы получения и оплаты билетов для каждого варианта заказа.
        ORDER_DELIVERY_CAPTION (dict): Подписи способов получения билетов.
        ORDER_PAYMENT_CAPTION (dict): Подписи способов оплаты.
        ORDER_OVERALL_CAPTION (dict): Подписи разных вариантов вычисления общей суммы заказа.
        ORDER_STATUS_CAPTION (dict): Подписи статусов заказа и их визуальное оформление.
        CUSTOMER_ATTRIBUTES (tuple): Реквизиты покупателя, которые необходимо сохранять в cookies браузера.
        OVERALL_EXTRA_MULTIPLIER (int): Число, до которого округляется общая сумма заказа с сервисным сбором и с оффлайн-оплатой.

    Attributes:
        logger (logging.Logger): Логгер для записи информации о текущей операции.

        event_title (str): Название события.
        event_url (str): URL события на сайте (для обратной ссылки в случае ошибки).

        city_title (str): Название города.
        city_timezone (pytz.tzfile): Часовой пояс города сайта.

        domain_id (int): Идентификатор сайта.
        domain_title (str): Название сайта.
        domain_slug (str): Псевдоним (поддомен) сайта.

        ticket_service (dict): Информация о сервисе продажи билетов.
        payment_service (dict): Информация о сервисе онлайн-оплаты.

        markup (dict): Различные возможные наценки при оформлении заказа.

        payment_url (str): URL платёжной формы при онлйн-оплате.

        order (dict): Параметры текущего предварительного резерва или созданного заказа.
            Содержимое ``order``:
                * order_uuid (uuid.UUID): UUID заказа.
                * order_id (int): Идентификатор заказа (после его успешного создания и записи в БД), иначе ``None``.

                * domain_slug (str): Псевдоним (поддомен) сайта.
                * city_timezone (pytz.tzfile): Часовой пояс города сайта.

                * ticket_service_id (str): Идентификатор сервиса продажи билетов.

                * event_uuid (uuid.UUID): UUID события.
                * event_id (int): Идентификатор события.

                * customer (dict): Реквизиты покупателя.
                    Содержимое ``customer``:
                        * name (str): ФИО покупателя.
                        * phone (str): Телефон покупателя.
                        * email (str): Электронная почта покупателя.
                        * address (str): Адрес доставки (если она нужна), иначе ``None``.

                * delivery (str): Способ получения заказа.
                    Возможные значения ``delivery``:
                        * self: Получение покупателем в кассе.
                        * courier: Доставка курьером.
                        * email: Электронный билет.
                * payment (str): Способ оплаты заказа (cash | online).
                    Возможные значения ``payment``:
                        * cash: Оффлайн-оплата (наличными или банковской картой на месте).
                        * online: Онлайн-оплата.

                * extra (decimal.Decimal): Процент сервисного сбора с каждого билета в заказе.
                * courier_price (decimal.Decimal): Стоимость доставки курьером (если она используется).
                * commission (decimal.Decimal): Процент комиссии сервиса онлайн-оплаты (если он используется).

                * payment_id (str): Идентификатор ронлайн-оплаты (если она используется), иначе ``None``.

                * status (str): Статус заказа.
                    Возможные значения ``status``:
                        * reserved: Предварительные резерв.
                        * ordered: Созданный заказ (в процессе оформления).
                        * approved: Успешно подтвёрждённый заказ.
                        * cancelled: Отменённый заказ.
                        * refunded: Заказ с возвратом полной/частичной стоимости покупателю.

                * tickets_count (int): Число билетов в заказе.
                * tickets (dict): Словарь, содежащий словари с информацией о билетах в заказе. Ключи словаря - идентификаторы билета в сервисе продажи билетов ``ticket_id``.
                    Содержимое словарей в ``tickets``:
                        * ticket_uuid (uuid.UUID): UUID билета.
                        * sector_id (int): Идентификатор сектора.
                        * sector_title (str): Название сектора.
                        * row_id (int): Идентификатор ряда.
                        * seat_id (int): Идентификатор места.
                        * seat_title (str): Название места.
                        * bar_code (str): Штрих-код билета.
                * total (decimal.Decimal): Сумма цен на все билеты в заказе.
                * overall (decimal.Decimal): Общая сумма заказа (с учётом возможных наценок/скидок).
                * overall_header (str): Заголовок для общей суммы заказа (с учётом возможных наценок/скидок).
    """
    ORDER_TYPE = ('self_online', 'email_online', 'self_cash', 'courier_cash',)
    ORDER_TYPE_MAPPING = {
        'self_online':  {'delivery': 'self',    'payment': 'online', },
        'email_online': {'delivery': 'email',   'payment': 'online', },
        'self_cash':    {'delivery': 'self',    'payment': 'cash', },
        'courier_cash': {'delivery': 'courier', 'payment': 'cash', },
    }
    ORDER_DELIVERY_CAPTION = {
        None:      '-',
        'self':    'получение в кассе',
        'courier': 'доставка курьером',
        'email':   'электронный билет',
    }
    ORDER_PAYMENT_CAPTION = {
        None:     '-',
        'cash':   'оплата при получении',
        'online': 'онлайн-оплата',
    }
    ORDER_OVERALL_CAPTION = {
        'overall_total':            'Общая сумма заказа',
        'overall_extra':            'Всего с учётом сервисного сбора',
        'overall_courier':          'Всего с учётом доставки курьером',
        'overall_courier_extra':    'Всего с учётом доставки курьером и сервисного сбора',
        'overall_commission':       'Всего с учётом комиссии платёжной системы',
        'overall_commission_extra': 'Всего с учётом комиссии платёжной системы и сервисного сбора',
    }
    ORDER_STATUS_CAPTION = {
        # Статус предварительного резерва мест, когда заказ ещё не создан
        'reserved':  {'color': 'black',  'description': 'предварительный резерв'},
        # Статусы созданного заказа
        'ordered':   {'color': 'blue',   'description': 'создан'},
        'cancelled': {'color': 'red',    'description': 'отменён'},
        'approved':  {'color': 'green',  'description': 'успешно завершён'},
        'refunded':  {'color': 'violet', 'description': 'возвращён'},
    }
    CUSTOMER_ATTRIBUTES = ('name', 'phone', 'email', 'address', 'order_type')
    OVERALL_EXTRA_MULTIPLIER = 50

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(kwargs.get('logger', 'bezantrakta.reserve'))

        # Получение существующего или создание нового пустого предварительного резерва
        if 'order_uuid' in kwargs and kwargs['order_uuid']:
            self.get(kwargs['order_uuid'])
        else:
            self.order = {}

            self.order['event_uuid'] = kwargs.get('event_uuid', None)
            self.order['order_uuid'] = uuid.uuid4()

            # Получение реквизитов покупателя
            if 'customer' in kwargs and kwargs['customer']:
                self.order['customer'] = {}
                for attr in OrderBasket.CUSTOMER_ATTRIBUTES:
                    self.order['customer'][attr] = kwargs['customer'].get(attr, None)
            else:
                self.order['customer'] = {attr: None for attr in OrderBasket.CUSTOMER_ATTRIBUTES}

            self.order['delivery'] = None
            self.order['payment'] = None

            self.order['status'] = 'reserved'

            self.order['tickets'] = {}
            self.order['tickets_count'] = 0
            self.order['total'] = self.decimal_price(0)

            self.order['overall'] = self.decimal_price(0)

        self.post_init()

        if not kwargs['order_uuid']:
            self.update()

    def __str__(self):
        return '{cls}({order_uuid})'.format(
            cls=self.__class__.__name__,
            order_uuid=self.order['order_uuid'],
        )

    def __repr__(self):
        return '{cls}({order_uuid})'.format(
            cls=self.__class__.__name__,
            order_uuid=self.order['order_uuid'],
        )

    def post_init(self):
        if self.order and self.order['event_uuid']:
            # Информация о событии
            event = cache_factory('event', self.order['event_uuid'])

            self.order['event_id'] = event['ticket_service_event']

            self.event_title = event['event_title']
            self.event_url = event['url']

            # Информация о сайте
            domain = cache_factory('domain', event['domain_slug'])

            self.city_title = domain['city_title']
            self.city_timezone = domain['city_timezone']
            self.domain_id = domain['domain_id']
            self.domain_title = domain['domain_title']
            self.domain_slug = event['domain_slug']

            # Получение реквизитов покупателя ???
            if 'customer' not in self.order:
                self.order['customer'] = {}
                for attr in OrderBasket.CUSTOMER_ATTRIBUTES:
                    self.order['customer'][attr] = (
                        self.order[attr] if
                        attr in self.order and self.order[attr] else
                        None
                    )

            if not self.order['customer']['address']:
                self.order['customer']['address'] = self.city_title

            self.order['delivery_caption'] = OrderBasket.ORDER_DELIVERY_CAPTION[self.order['delivery']]
            self.order['payment_caption'] = OrderBasket.ORDER_PAYMENT_CAPTION[self.order['payment']]

            self.order['status_color'] = OrderBasket.ORDER_STATUS_CAPTION[self.order['status']]['color']
            self.order['status_caption'] = OrderBasket.ORDER_STATUS_CAPTION[self.order['status']]['description']

            # Формирование упорядоченного списка билетов в заказе для вывода
            tickets_list = [t for tid, t in self.order['tickets'].items()]
            self.order['tickets_list'] = sorted(
                tickets_list, key=itemgetter('sector_title', 'row_id', 'seat_id', 'price')
            )

            self.ticket_service = {}
            self.ticket_service['id'] = event['ticket_service_id']
            # Информация о сервисе продажи билетов
            ticket_service = cache_factory('ticket_service', self.ticket_service['id'])

            if ticket_service and ticket_service['is_active']:
                self.ticket_service['title'] = ticket_service['title']
                self.ticket_service['max_seats_per_order'] = ticket_service['settings']['max_seats_per_order']
                self.ticket_service['heartbeat_timeout'] = ticket_service['settings']['heartbeat_timeout']
                self.ticket_service['seat_timeout'] = ticket_service['settings']['seat_timeout']

                self.ticket_service['order_email'] = {}
                self.ticket_service['order_email']['user'] = ticket_service['settings']['order_email']['user']
                self.ticket_service['order_email']['pswd'] = ticket_service['settings']['order_email']['pswd']

                self._ts = ticket_service['instance']

            self.payment_service = {}
            self.payment_service['id'] = event['payment_service_id']
            # Информация о сервисе онлайн-оплаты
            payment_service = cache_factory(
                'payment_service', self.payment_service['id'],
                domain_slug=event['domain_slug']
            )

            if payment_service and payment_service['is_active']:
                self.payment_service['title'] = payment_service['title']
                self.payment_service['description'] = payment_service['settings']['description']
                self.payment_service['timeout'] = payment_service['settings']['timeout']
                self.payment_service['success_url'] = payment_service['settings']['init']['success_url']
                self.payment_service['error_url'] = payment_service['settings']['init']['error_url']

                self._ps = payment_service['instance']

            # Различные возможные наценки при оформлении заказа
            self.markup = {}
            # Процент сервисного сбора на каждый из билетов в заказе
            self.markup['extra'] = event['settings']['extra']
            # Стоимость доставки курьером, если она используется
            self.markup['courier_price'] = self.decimal_price(ticket_service['settings']['courier_price'])
            # Процент комиссии сервиса онлайн-оплаты, если он используется
            self.markup['commission'] = self.decimal_price(
                payment_service['settings']['commission'] if payment_service else 0
            )

            self.get_overall()

    def get(self, order_uuid):
        # Получить существующий заказ
        self.order = cache_factory('order', order_uuid)

    def update(self):
        # Обновить существующий заказ, используя изменённое ранее значение self.order
        self.get_overall()
        self.order['updated'] = self.now()
        self.order = cache_factory('order', self.order['order_uuid'], obj=self.order, reset=True)

        self.post_init()

    def delete(self):
        # Полностью удалить существующий заказ
        cache_factory('order', self.order['order_uuid'], delete=True)

    def log(self):
        """Логирование информации о полученном предварительном резерве или созданном заказе."""
        self.logger.info('Сайт: {title} ({id})'.format(title=self.domain_title, id=self.domain_id))
        self.logger.info('Сервис продажи билетов: {title} ({id})'.format(
            title=self.ticket_service['title'],
            id=self.ticket_service['id']
        ))

        self.logger.info('UUID события: {}'.format(self.order['event_uuid']))
        self.logger.info('Идентификатор события: {}'.format(self.order['event_id']))
        self.logger.info('Название события: {}'.format(self.event_title))

        if self.order['customer']:
            self.logger.info('\nРеквизиты покупателя:')
            self.logger.info('ФИО: {}'.format(self.order['customer']['name']))
            self.logger.info('Email: {}'.format(self.order['customer']['email']))
            self.logger.info('Телефон: {}'.format(self.order['customer']['phone']))

        if self.order['status'] == 'reserved':
            self.logger.info('Предварительный резерв:')
        else:
            self.logger.info('Заказ:')

        self.logger.info('UUID: {}'.format(self.order['order_uuid']))
        self.logger.info('Билеты:')
        if self.order['tickets_count'] > 0:
            for ticket_id in self.order['tickets']:
                self.logger.info('* {}'.format(self.order['tickets'][ticket_id]))
        else:
            self.logger.info('Билеты: \{\}')
        self.logger.info('Число билетов: {}'.format(self.order['tickets_count']))
        self.logger.info('Сумма: {}'.format(self.order['total']))
        self.logger.info('Всего: {}'.format(self.order['overall']))

        self.logger.info('Получение билетов: {}'.format(self.order['delivery_caption']))
        if self.order['delivery'] == 'courier':
            self.logger.info('Адрес доставки: {}'.format(self.order['customer']['address']))
        self.logger.info('Оплата билетов: {}'.format(self.order['payment_caption']))

    def ticket_toggle(self, ticket_id, is_fixed, action):
        response = {}

        if action == 'add':
            self.logger.info('\nДействие: добавить')
        elif action == 'remove':
            self.logger.info('\nДействие: удалить')

        add_condition = action == 'add' and self.order['tickets_count'] < self.ticket_service['max_seats_per_order']
        remove_condition = action == 'remove' and self.order['tickets_count'] > 0

        if add_condition or remove_condition:
            # Параметры для отправки запроса к сервису продажи билетов
            params = {
                'event_id':   self.order['event_id'],
                'order_uuid': self.order['order_uuid'],
                'ticket_id':  ticket_id,
                'action':     action
            }

            # Универсальный метод для работы с предварительным резервом мест
            reserve = self._ts.reserve(**params)
            self.logger.info('\nreserve: {}'.format(reserve))

            if add_condition:
                seats_and_prices = cache_factory('seats_and_prices', self.order['event_uuid'])
                if not seats_and_prices:
                    response['success'] = False
                    response['message'] = 'Не получена информация о билетах в событии'
                    return response
                ticket = seats_and_prices['seats'].get(ticket_id, None)
                self.logger.info('\nticket: {}'.format(ticket))
                if not ticket:
                    response['success'] = False
                    response['message'] = 'Не получена информация о билете'
                    return response

                if reserve['success']:
                    self.order['tickets'][ticket_id] = {
                        'ticket_uuid':  uuid.uuid4(),
                        'ticket_id':    ticket_id,
                        'sector_id':    ticket['sector_id'],
                        'sector_title': ticket['sector_title'],
                        'row_id':       ticket['row_id'],
                        'seat_id':      ticket['seat_id'],
                        'seat_title':   ticket['seat_title'],
                        'price':        self.decimal_price(ticket['price']),
                        'price_order':  ticket['price_order'],
                        'is_fixed':     bool(is_fixed),
                        'added':        self.now(),
                    }
                    self.order['tickets_count'] += 1
                    self.order['total'] += self.decimal_price(ticket['price'])
            elif remove_condition:
                # Даже если при удалении билета получен НЕуспешный ответ -
                # билет в любом случае удаляется из предварительного резерва
                try:
                    ticket_price = self.order['tickets'][ticket_id]['price']
                except KeyError:
                    pass
                else:
                    del self.order['tickets'][ticket_id]
                    self.order['tickets_count'] -= 1
                    self.order['total'] -= self.decimal_price(ticket_price)

            self.update()

            if reserve['success']:
                response['success'] = True
                response['message'] = 'Билет успешно удалён из резерва'
                response['ticket_id'] = ticket_id
                response['action'] = action
                response['tickets'] = self.order['tickets']
                response['tickets_count'] = self.order['tickets_count']
                response['total'] = self.order['total']
            else:
                response['success'] = False
                response['message'] = reserve['message']
        else:
            response['success'] = False
            response['message'] = 'Невозможно провести резерв билета'

        return response

    def tickets_clear(self):
        """Освобождение билетов и удаление предварительного резерва.

        Returns:
            dict: Description
        """
        self.logger.info('\nОтмена предыдущего предварительного резерва...')

        response = {}
        response['success'] = True
        response['tickets'] = {}

        if self.order['tickets_count'] > 0:
            tickets = self.order['tickets'].copy()

            for ticket_id, ticket in tickets.items():
                remove = self.ticket_toggle(ticket_id, True, 'remove')

                response['tickets'][ticket_id] = ticket

                if remove['success']:
                    response['tickets'][ticket_id]['removed'] = True
                    self.logger.info('    Билет успешно удалён из предварительного резерва')
                else:
                    response['tickets'][ticket_id]['removed'] = False
                    self.logger.info('    Билет НЕ удалось удалить из предварительного резерва')

                # Задержка в несколько секунд во избежание возможных ошибок
                sleep(randint(2, 5))

        self.delete()

        response['message'] = 'Старый предварительный резерв успешно удалён'

        return response

    def tickets_check(self, status):
        """Проверка состояния билетов в предварительном резерве или созданном заказе."""
        if status == 'reserved':
            self.logger.info('\nПроверка состояния билетов в предварительном резерве...')
        elif status == 'ordered':
            self.logger.info('\nПроверка состояния билетов в созданном заказе...')
        elif status == 'approved':
            self.logger.info('\nПроверка состояния билетов в подтверждённом заказе...')

        for ticket_id in self.order['tickets']:
            params = {
                'event_id':  self.order['event_id'],
                'ticket_id': ticket_id,
            }

            ticket_status = self._ts.ticket_status(**params)
            self.logger.info('    ticket_status: {}'.format(ticket_status))

            self.order['tickets'][ticket_id]['status'] = ticket_status['status']

            # Если статус билета совпадает с запрошенным или не требует проверки
            if ticket_status['success'] or ticket_status['status'] in (status, 'bypass',):
                self.logger.info('    🎫: {}'.format(self.order['tickets'][ticket_id]))
            # Если статус билета НЕ совпадает с запрошенным
            else:
                del self.order['tickets'][ticket_id]
                self.order['tickets_count'] -= 1
                self.order['total'] -= self.decimal_price(self.order['tickets'][ticket_id]['price'])

                self.logger.error('    Ошибка с билетом {}'.format(ticket_id))

        self.update()

    def order_type_default(self, order_type):
        """Предварительный выбор типа заказа из списка активных в конкретном событии,
        если заказов ранее не было или если выбранный ранее тип заказа неактивен в конкретном событии."""
        default_order_type = None

        # Информация о событии
        event = cache_factory('event', self.order['event_uuid'])
        # Информация о сервисе продажи билетов
        ticket_service = cache_factory('ticket_service', self.ticket_service['id'])
        # Информация о сервисе онлайн-оплаты
        payment_service = cache_factory(
            'payment_service', self.payment_service['id'],
            domain_slug=event['domain_slug']
        )

        # Все типы заказа билетов для выбора (настройки в сервисе продажи билетов и в событии)
        order_types = OrderedDict()
        for ot in self.ORDER_TYPE:
            order_types.update(
                {
                    ot: {
                        'ticket_service': ticket_service['settings']['order'][ot],
                        'event':                   event['settings']['order'][ot],
                    }
                }
            )

        # Активные типы заказа билетов в конкретном событии
        order_types_active = tuple(
            ot for ot in order_types.keys() if
            order_types[ot]['ticket_service'] is True and order_types[ot]['event'] is True and
            (payment_service or not ot.endswith('_online'))
        )
        # Типы заказа билетов с онлайн-оплатой НЕ включаются в список активных,
        # если к текущему сервису продажи билетов НЕ привязан никакой сервис онлайн-оплаты

        # Выбор первого доступного типа заказа по порядку,
        # если он НЕ был выбран ранее или если выбранный ранее тип заказа в текущем событии отключен
        if not order_type or order_type not in order_types_active:
            for ot in order_types.keys():
                if ot in order_types_active:
                    default_order_type = ot
                    break
        else:
            default_order_type = order_type

        return default_order_type

    def order_type_change(self, customer, order_type):
        # Обновление типа получения и типа оплаты билетов
        self.order['delivery'] = OrderBasket.ORDER_TYPE_MAPPING[order_type]['delivery']
        self.order['payment'] = OrderBasket.ORDER_TYPE_MAPPING[order_type]['payment']

        # Обновление реквизитов покупателя
        self.order['customer']['name'] = customer['name']
        self.order['customer']['phone'] = customer['phone']
        self.order['customer']['email'] = customer['email']
        self.order['customer']['address'] = customer['address']
        self.order['customer']['order_type'] = order_type

        self.update()

    def order_create(self):
        """Создание нового заказа в сервисе продажи билетов.

        Returns:
            dict: Информация о созданном заказе.
        """
        self.logger.info('\nСоздание заказа...')

        # Добавление опциональных параметров для возможной доставки курьером
        if self.order['delivery'] == 'courier':
            self.order['customer']['is_courier'] = True
            # self.order['customer']['address'] = self.order['customer']['address']
        else:
            self.order['customer']['is_courier'] = False
            self.order['customer']['address'] = None

        order_create = self._ts.order_create(
            event_id=self.order['event_id'],
            order_uuid=self.order['order_uuid'],
            customer=self.order['customer'],
            tickets=self.order['tickets']
        )

        if order_create['success']:
            self.order['status'] = 'ordered'
            self.logger.info('Статус заказа: {}'.format(self.order['status_caption']))

            self.order['order_id'] = order_create['order_id']
            self.logger.info('Идентификатор заказа: {}'.format(self.order['order_id']))

            # Получение штрих-кодов для билетов в заказе
            self.tickets_barcode(order_create)

        self.update()

        self.logger.info('\nbasket.order created: {}'.format(self.order))

        return order_create

    def tickets_barcode(self, order):
        """Получение штрих-кодов для билетов в заказе из ответа метода order_create."""
        for otid in order['tickets']:
            for tid in self.order['tickets']:
                if order['tickets'][otid]['ticket_uuid'] == self.order['tickets'][tid]['ticket_uuid']:
                    self.logger.info('\n{ot_uuid} == {tid_uuid}: {cond}'.format(
                        ot_uuid=order['tickets'][otid]['ticket_uuid'],
                        tid_uuid=self.order['tickets'][tid]['ticket_uuid'],
                        cond=order['tickets'][otid]['ticket_uuid'] == self.order['tickets'][tid]['ticket_uuid'])
                    )
                    self.order['tickets'][tid]['bar_code'] = (
                        order['tickets'][otid]['bar_code'] if
                        'bar_code' in order['tickets'][otid] and order['tickets'][otid]['bar_code'] else
                        # Если по каким-то причинам штрих-код не получен - он генерируется автоматически
                        ''.join([str(randint(0, 9)) for x in range(self._ts.bar_code_length)])
                    )
                    self.logger.info('t[bar_code]: {barcode}'.format(barcode=self.order['tickets'][tid]['bar_code']))
                else:
                    continue

        self.logger.info('\ntickets with bar_codes: {}'.format(self.order['tickets']))

    def order_create_db(self):
        response = {}

        # Сохранение созданного заказа в БД
        try:
            Order.objects.create(
                id=self.order['order_uuid'],
                ticket_service_id=self.ticket_service['id'],
                ticket_service_order=self.order['order_id'],
                event_id=self.order['event_uuid'],
                ticket_service_event=self.order['event_id'],
                datetime=timezone_now(),
                name=self.order['customer']['name'],
                email=self.order['customer']['email'],
                phone=self.order['customer']['phone'],
                address=self.order['customer']['address'],
                delivery=self.order['delivery'],
                payment=self.order['payment'],
                payment_id=None,
                status=self.order['status'],
                tickets_count=self.order['tickets_count'],
                total=self.order['total'],
                overall=self.order['overall'],
                domain_id=self.domain_id
            )
        except IntegrityError:
            response['success'] = False
            self.logger.critical('Такой заказ уже был добавлен в базу данных ранее!')
        else:
            response['success'] = True
            self.logger.info('\nЗаказ {order_uuid} сохранён в БД\n'.format(order_uuid=self.order['order_uuid']))

            for ticket_id in self.order['tickets']:
                try:
                    OrderTicket.objects.create(
                        id=self.order['tickets'][ticket_id]['ticket_uuid'],
                        order_id=self.order['order_uuid'],
                        ticket_service_id=self.ticket_service['id'],
                        ticket_service_order=self.order['order_id'],
                        is_fixed=self.order['tickets'][ticket_id]['is_fixed'],
                        is_punched=False,
                        bar_code=self.order['tickets'][ticket_id]['bar_code'],
                        ticket_id=ticket_id,
                        sector_id=self.order['tickets'][ticket_id]['sector_id'],
                        sector_title=self.order['tickets'][ticket_id]['sector_title'],
                        row_id=self.order['tickets'][ticket_id]['row_id'],
                        seat_id=self.order['tickets'][ticket_id]['seat_id'],
                        seat_title=self.order['tickets'][ticket_id]['seat_title'],
                        price=self.order['tickets'][ticket_id]['price'],
                        domain_id=self.domain_id
                    )
                except IntegrityError:
                    self.logger.critical('Невозможно добавить билет в БД!')
                else:
                    self.logger.info('Билет {} сохранён в БД'.format(self.order['tickets'][ticket_id]['ticket_uuid']))

        return response

    def payment_create(self):
        payment_create = self._ps.payment_create(
            event_uuid=self.order['event_uuid'],
            event_id=self.order['event_id'],
            order_uuid=self.order['order_uuid'],
            order_id=self.order['order_id'],
            customer=self.order['customer'],
            overall=self.order['overall'],
        )

        self.logger.info('payment_create: {}'.format(payment_create))

        # Успешный запрос на оплату
        if payment_create['success']:
            self.logger.info('\nСоздание новой онлайн-оплаты завершилось успешно')
        else:
            self.logger.info('\nСоздание новой онлайн-оплаты завершилось НЕуспешно')

        return payment_create

    def payment_create_db(self, payment_create):
        self.order['payment_id'] = payment_create['payment_id']
        self.payment_url = payment_create['payment_url']

        Order.objects.filter(id=self.order['order_uuid']).update(
            datetime=timezone_now(),
            payment_id=self.order['payment_id']
        )

        self.logger.info('Идентификатор оплаты: {}'.format(self.order['payment_id']))

        self.update()

    def payment_status(self):
        payment_status = self._ps.payment_status(payment_id=self.order['payment_id'])

        self.logger.info('Идентификатор оплаты: {}'.format(self.order['payment_id']))
        self.logger.info('payment_status: {}'.format(payment_status))

        if payment_status['success']:
            self.logger.info('\nОплата {payment_id} завершилась успешно'.format(
                payment_id=self.order['payment_id'])
            )
        else:
            self.logger.info('\nОплата {payment_id} завершилась НЕуспешно'.format(
                payment_id=self.order['payment_id'])
            )

        return payment_status

    def order_approve(self):
        # Подтвердить можно только созданный ранее заказ
        if self.order['status'] == 'ordered':
            self.logger.info('Подтверждение оплаты заказа в сервисе продажи билетов...')

            order_approve = self._ts.order_approve(
                event_id=self.order['event_id'],
                order_uuid=self.order['order_uuid'],
                order_id=self.order['order_id'],
                payment_id=self.order['payment_id'],
                payment_datetime=self.now(),
                tickets=self.order['tickets'],
            )

            self.logger.info('order_approve: {}'.format(order_approve))

            if order_approve['success']:
                # Обновление статуса заказа в БД
                self.order_status_db('approved')

                self.logger.info('Заказ {order_id} в сервисе продажи билетов отмечен как оплаченный'.format(
                    order_id=self.order['order_id']
                ))
            else:
                self.logger.info('Заказ {order_id} НЕ удалось отметить в сервисе продажи билетов как оплаченный'.format(
                    order_id=self.order['order_id']
                ))

            response = order_approve
        else:
            response = {}
            response['success'] = False
            response['message'] = 'Подтвердить можно только созданный ранее заказ'

        return response

    def order_cancel(self):
        # Отменить можно только созданный ранее заказ
        if self.order['status'] == 'ordered':
            self.logger.info('Отмена заказа в сервисе продажи билетов...')

            order_cancel = self._ts.order_cancel(
                event_id=self.order['event_id'],
                order_uuid=self.order['order_uuid'],
                order_id=self.order['order_id'],
                tickets=self.order['tickets'],
            )

            self.logger.info('order_cancel: {}'.format(order_cancel))

            if order_cancel['success']:
                # Обновление статуса заказа в БД
                self.order_status_db('cancelled')

                self.logger.info('Заказ {order_id} отменён в сервисе продажи билетов'.format(
                    order_id=self.order['order_id']
                ))
            else:
                self.logger.info('Заказ {order_id} НЕ удалось отменить в сервисе продажи билетов'.format(
                    order_id=self.order['order_id']
                ))

            response = order_cancel
        else:
            response = {}
            response['success'] = False
            response['message'] = 'Отменить можно только созданный ранее заказ'

        return response

    def order_refund(self, amount, reason=None):
        response = {}

        amount = self._ps.decimal_price(amount)

        self.logger.info('\nСумма возврата: {} р.'.format(amount))
        self.logger.info('Причина возврата: {}.'.format(reason))

        # Возврат возможен только для подтверждённых заказов
        if self.order['status'] == 'approved':
            # Проверка состояния билетов в заказе (на всякий случай)
            self.tickets_check('approved')

            # Возврат заказа в сервисе продажи билетов
            self.logger.info('\nВозврат заказа в сервисе продажи билетов...')

            order_refund = self._ts.order_refund(
                order_id=self.order['order_id'],
                payment_id=self.order['payment_id'],
                amount=amount,
                reason=reason,
            )
            # order_refund = {'success': True, 'amount': amount}
            # order_refund = {'success': False, 'code': 2000, 'message': 'Order has been already deleted'}

            self.logger.info('order_refund: {}'.format(order_refund))

            if order_refund['success']:
                order_message = 'Заказ {order_id} успешно возвращён в сервисе продажи билетов'.format(
                    order_id=self.order['order_id']
                )
            else:
                order_message = 'Заказ {order_id} в сервисе продажи билетов возвратить НЕ удалось'.format(
                    order_id=self.order['order_id']
                )
            self.logger.info(order_message)

            # Возврат заказа в сервисе онлайн-оплаты
            self.logger.info('\nВозврат заказа в сервисе онлайн-оплаты...')

            payment_refund = self._ps.payment_refund(
                event_uuid=self.order['event_uuid'],
                event_id=self.order['event_id'],
                order_uuid=self.order['order_uuid'],
                order_id=self.order['order_id'],
                customer=self.order['customer'],
                payment_id=self.order['payment_id'],
                amount=amount,
            )
            # payment_refund = {'success': True, 'amount': amount}
            # payment_refund = {'success': False, 'code': 5, 'message': 'Неверная сумма'}

            self.logger.info('payment_refund: {}'.format(payment_refund))

            if payment_refund['success']:
                payment_message = 'Заказ {order_id} успешно возвращён в сервисе онлайн-оплаты'.format(
                    order_id=self.order['order_id']
                )
            else:
                payment_message = 'Заказ {order_id} в сервисе онлайн-оплаты возвратить НЕ удалось'.format(
                    order_id=self.order['order_id']
                )
            self.logger.info(payment_message)

            if order_refund['success'] and payment_refund['success']:
                # Обновление статуса заказа в БД
                self.order_status_db('refunded')

                response['success'] = True
                response['message'] = 'Возврат по заказу № {order_id} проведён успешно'.format(
                    order_id=self.order['order_id']
                )
            else:
                response['success'] = False

                if order_refund['success']:
                    message = '{} {}'.format(
                        payment_refund.get('code', ''), payment_refund.get('message')
                    )
                    response['message'] = 'Возврат по заказу № {order_id} проведён успешно только в сервисе продажи билетов. {message}'.format(
                        order_id=self.order['order_id'], message=message.strip()
                    )
                elif payment_refund['success']:
                    message = '{} {}'.format(
                        payment_refund.get('code', ''), payment_refund.get('message')
                    )
                    response['message'] = 'Возврат по заказу № {order_id} проведён успешно только в сервисе онлайн-оплаты. {message}'.format(
                        order_id=self.order['order_id'], message=message.strip()
                    )
                else:
                    order_message = '{} {}'.format(
                        order_refund.get('code', ''), order_refund.get('message')
                    )
                    payment_message = '{} {}'.format(
                        payment_refund.get('code', ''), payment_refund.get('message')
                    )
                    message = '{} {}'.format(
                        order_message.strip(), payment_message.strip()
                    )
                    response['message'] = 'Возврат НЕ удалось завершить успешно. {}'.format(
                        message.strip()
                    )
        else:
            response['success'] = False
            response['message'] = 'Возврат возможен только для подтверждённых заказов'

        return response

    def order_status_db(self, status):
        """Сохранение статуса заказа в БД."""
        self.order['status'] = status
        self.order['status_color'] = OrderBasket.ORDER_STATUS_CAPTION[self.order['status']]['color']
        self.order['status_caption'] = OrderBasket.ORDER_STATUS_CAPTION[self.order['status']]['description']

        Order.objects.filter(id=self.order['order_uuid']).update(status=self.order['status'])

        self.logger.info('\nСтатус заказа: {}'.format(self.order['status_caption']))

        self.update()

    def email_prepare(self):
        # Отправка email администратору и покупателю
        email_from = {}
        email_from['user'] = self.ticket_service['order_email']['user']
        email_from['pswd'] = self.ticket_service['order_email']['pswd']
        email_from['connection'] = EmailBackend(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=email_from['user'],
            password=email_from['pswd'],
            use_tls=settings.EMAIL_USE_TLS,
        )

        # Информация о событии
        event = cache_factory('event', self.order['event_uuid'])
        # Информация о сайте
        domain = cache_factory('domain', event['domain_slug'])
        # Информация о сервисе продажи билетов
        ticket_service = cache_factory('ticket_service', self.ticket_service['id'])
        # Информация о сервисе онлайн-оплаты
        payment_service = cache_factory(
            'payment_service', self.payment_service['id'],
            domain_slug=event['domain_slug']
        )

        email_context = {
            'domain':          domain,
            'event':           event,
            'ticket_service':  ticket_service,
            'payment_service': payment_service,
            'order':           self.order,
            'customer':        self.order['customer']
        }

        response = {}
        response['from'] = email_from
        response['context'] = email_context

        return response

    def email_admin(self):
        email = self.email_prepare()

        admin_email = EmailMessage(
            'order/email_admin.tpl',
            email['context'],
            email['from']['user'],
            (email['from']['user'],),
            connection=email['from']['connection']
        )

        try:
            sender = admin_email.send()
        except SMTPException as exc:
            sender = 0
            sender_exception = exc

        if bool(sender):
            message = 'Email-уведомление администратору отправлено'

            self.logger.info(message)

            return {
                'success': True,
                'message': message,
            }
        else:
            message = 'НЕ удалось отправить email-уведомление администратору.\n{}'.format(sender_exception)

            self.logger.info(message)

            return {
                'success': False,
                'message': message,
            }

    def email_customer(self):
        email = self.email_prepare()

        customer_email = EmailMessage(
            'order/email_customer.tpl',
            email['context'],
            email['from']['user'],
            (self.order['customer']['email'],),
            connection=email['from']['connection']
        )

        # Опциональная генерация электронных билетов и их вложение в письмо покупателю
        if self.order['delivery'] == 'email':
            self.logger.info('\nСоздание электронных PDF-билетов...')
            for ticket_id in self.order['tickets']:
                # Формирование контекста для генерации PDF-билета (билет + событие + order_id)
                ticket_context = self.order['tickets'][ticket_id]
                ticket_context.update(email['context']['event'])
                ticket_context['order_id'] = self.order['order_id']

                self.logger.info('\nИнформация о билете: {}'.format(ticket_context))

                pdf_ticket_file = render_eticket(ticket_context, self.logger)
                customer_email.attach_file(pdf_ticket_file, mimetype='application/pdf')

        try:
            sender = customer_email.send()
        except SMTPException as exc:
            sender = 0
            sender_exception = exc

        if bool(sender):
            message = 'Email-уведомление покупателю отправлено'

            self.logger.info(message)

            return {
                'success': True,
                'message': message,
            }
        else:
            message = 'НЕ удалось отправить email-уведомление покупателю.\n{}'.format(sender_exception)

            self.logger.info(message)

            return {
                'success': False,
                'message': message,
            }

    def get_overall(self):
        """Получение общей суммы заказа и её подписи в зависимости от возможных наценок/скидок."""
        order_type = self.order['customer']['order_type'] if 'customer' in self.order else 'self_cash'
        extra = self.markup['extra'][order_type] if order_type in self.markup['extra'] else 0

        # Для любого типа заказа без дополнительных условий - с учётом сервисного сбора (если он задан)
        if extra > 0:
            self.order['overall'] = self.overall_with_extra(extra)
            self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_extra']
        # Иначе - сумма цен на билеты
        else:
            self.order['overall'] = self.order['total']
            self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_total']

        # При доставке курьером - с учётом стоимости доставки курьером (если она задана)
        if self.order['delivery'] == 'courier':
            if extra > 0:
                # С учётом доставки курьером и сервисного сбора
                if self.markup['courier_price'] > 0:
                    self.order['overall'] = self.overall_plus_courier_price()
                    self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_courier_extra']
                # Иначе - с учётом сервисного сбора
                # else:
                    # self.order['overall'] = self.overall_with_extra(extra)
                    # self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_extra']
            else:
                # С учётом доставки курьером
                if self.markup['courier_price'] > 0:
                    self.order['overall'] = self.overall_plus_courier_price()
                    self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_courier']
                # Иначе - сумма цен на билеты
                # else:
                    # self.order['overall'] = self.order['total']
                    # self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_total']

        # При онлайн-оплате - с учётом комиссии сервиса онлайн-оплаты (если она задана)
        if self.order['payment'] == 'online':
            if extra > 0:
                # С учётом комиссии платёжной системы и сервисного сбора
                if self.markup['commission'] > 0:
                    self.order['overall'] = self.overall_with_commission()
                    self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_commission_extra']
                # Иначе - также с учётом комиссии платёжной системы и сервисного сбора
                else:
                    self.order['overall'] = self.overall_with_extra(extra)
                    self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_commission_extra']
            else:
                # С учётом комиссии платёжной системы
                if self.markup['commission'] > 0:
                    self.order['overall'] = self.overall_with_commission()
                    self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_commission']
                # Иначе - сумма цен на билеты
                # else:
                    # self.order['overall'] = self.order['total']
                    # self.order['overall_header'] = OrderBasket.ORDER_OVERALL_CAPTION['overall_total']

        # Пересчёт общей суммы заказа для удобства оффлайн-оплаты (кратно значению в OVERALL_EXTRA_MULTIPLIER)
        if extra > 0 and self.order['payment'] == 'cash':
            overall = self.order['overall']
            multiplier = OrderBasket.OVERALL_EXTRA_MULTIPLIER

            self.order['overall'] = (overall - (overall % multiplier)) + multiplier

    def overall_with_extra(self, extra):
        """Общая сумма заказа с учётом сервисного сбора.

        Если процент сервисного сбора больше ``0``,
        то к сумме заказа добавляется указанный процент от цены каждого из билетов в заказе.
        Если процент сервисного сбора равен ``0``, мы получаем ту же самую сумму.

        Args:
            extra (decimal.Decimal): Процент сервисного сбора для конкретного типа заказа.

        Returns:
            decimal.Decimal: Общая сумма заказа ``overall``.
        """
        overall_with_extra = self.order['total']
        if extra > 0:
            for ticket_id in self.order['tickets']:
                ticket_price = self.order['tickets'][ticket_id]['price']
                overall_with_extra += (self.decimal_price(ticket_price) * extra) / self.decimal_price(100)
        return self.decimal_price(overall_with_extra)

    def overall_plus_courier_price(self):
        """Общая сумма заказа с учётом стоимости доставки курьером.

        Если стоимость доставки курьером больше ``0``, то она добавляется к сумме заказа.
        Если стоимость доставки курьером равна ``0``, мы получаем ту же самую сумму.

        Returns:
            decimal.Decimal: Общая сумма заказа ``overall``.
        """
        return self.decimal_price(self.order['overall'] + self.markup['courier_price'])

    def overall_with_commission(self):
        """Общая сумма заказа при онлайн-оплате.

        Если комиссия сервиса онлайн-оплаты не равна ``0``,
        то к сумме заказа добавляется указанный процент от самой суммы заказа.
        Если комиссия равна ``0``, мы получаем ту же самую сумму.

        Returns:
            decimal.Decimal: Общая сумма заказа ``overall``.
        """
        return self.decimal_price(
            self.order['overall'] + ((self.order['overall'] * self.markup['commission']) / self.decimal_price(100))
        )

    def decimal_price(self, value):
        """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа ``Decimal``.

        Args:
            value (str): Входное значение (в любом случае строка - для обхода проблем с округлением ``float``).

        Returns:
            decimal.Decimal: Денежная сумма.
        """
        return Decimal(str(value)).quantize(Decimal('1.00'))

    def now(self):
        now = timezone_now()
        return now.astimezone(pytz.timezone(self.city_timezone))
