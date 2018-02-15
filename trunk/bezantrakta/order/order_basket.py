import logging
import pytz
import uuid
from decimal import Decimal

from bezantrakta.order.settings import ORDER_TYPE_MAPPING, ORDER_OVERALL_CAPTION

from project.cache import cache_factory
from project.shortcuts import timezone_now


class OrderBasket():
    """Класс для работы с предварительными резервами и созданными заказами.

    Проводит определённые операции с заказом, получая информацию о нём из кэша.

    Attributes:
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
    def __init__(self, **kwargs):
        self._logger = logging.getLogger('bezantrakta.reserve')

        # Получение существующего или создание нового пустого предварительного резерва
        if 'order_uuid' in kwargs and kwargs['order_uuid']:
            self.get_order(kwargs['order_uuid'])
        else:
            # Информация о событии
            event = cache_factory('event', kwargs['event_uuid']) if 'event_uuid' in kwargs else None

            self.order = {}

            self.order['order_uuid'] = uuid.uuid4()
            self.order['order_id'] = None

            if event:
                self.order['domain_slug'] = event['domain_slug']
                self.order['city_timezone'] = event['city_timezone']
                self.order['ticket_service_id'] = event['ticket_service_id']
                self.order['event_uuid'] = event['event_uuid']
                self.order['event_id'] = event['ticket_service_event']
            else:
                self.order['domain_slug'] = None
                self.order['city_timezone'] = 'Europe/Moscow'
                self.order['ticket_service_id'] = None
                self.order['event_uuid'] = None
                self.order['event_id'] = None

            # Получение реквизитов покупателя
            customer_attributes = ('name', 'phone', 'email', 'address', 'order_type')
            if 'customer' in kwargs and kwargs['customer']:
                self.order['customer'] = {}
                for attr in customer_attributes:
                    self.order['customer'][attr] = (
                        kwargs['customer'][attr] if
                        attr in kwargs['customer'] and kwargs['customer'][attr] else
                        None
                    )
            else:
                self.order['customer'] = {attr: None for attr in customer_attributes}

            self.order['delivery'] = None
            self.order['payment'] = None

            self.order['extra'] = 0
            self.order['courier_price'] = 0
            self.order['commission'] = 0

            self.order['payment_id'] = None

            self.order['status'] = 'reserved'

            self.order['tickets'] = {}
            self.order['tickets_count'] = 0
            self.order['total'] = self.decimal_price(0)

            self.order['overall'] = self.decimal_price(0)
            self.order['overall_header'] = ORDER_OVERALL_CAPTION['overall_total']

            self.update_order()

        if self.order:
            # Информация о сервисе продажи билетов
            ticket_service = cache_factory('ticket_service', self.order['ticket_service_id'])

            self._max_seats_per_order = ticket_service['settings']['max_seats_per_order']
            self._ts = ticket_service['instance']

    def __str__(self):
        return '{cls}({order_uuid})'.format(
            cls=self.__class__.__name__,
            order_uuid=self.order['order_uuid'],
        )

    def get_order(self, order_uuid):
        # Получить существующий заказ
        self.order = cache_factory('order', order_uuid)

    def update_order(self):
        # Создать новый или обновить существующий заказ, используя self.order
        self.order['updated'] = self.now()
        self.order = cache_factory('order', self.order['order_uuid'], obj=self.order, reset=True)

    def delete_order(self):
        # Полностью удалить существующий заказ
        cache_factory('order', self.order['order_uuid'], delete=True)

    def toggle_ticket(self, ticket_id, action):
        response = {}

        add_condition = action == 'add' and self.order['tickets_count'] < self._max_seats_per_order
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
            # self._logger.info('\nreserve: {}'.format(reserve))

            if add_condition:
                seats_and_prices = cache_factory('seats_and_prices', self.order['event_uuid'])
                ticket = seats_and_prices['seats'][ticket_id]
                # self._logger.info('\nticket: {}'.format(ticket))

                if reserve['success']:
                    self.order['tickets'][ticket_id] = {
                        'ticket_uuid':  uuid.uuid4(),
                        'sector_id':    ticket['sector_id'],
                        'sector_title': ticket['sector_title'],
                        'row_id':       ticket['row_id'],
                        'seat_id':      ticket['seat_id'],
                        'seat_title':   ticket['seat_title'],
                        'price':        self.decimal_price(ticket['price']),
                        'price_order':  ticket['price_order'],
                        'added':        self.now(),
                    }
                    self.order['tickets_count'] += 1
                    self.order['total'] += self.decimal_price(ticket['price'])
            elif remove_condition:
                # Даже если при удалении билета получен НЕуспешный ответ -
                # билет в любом случае удаляется из предварительного резерва
                ticket = self.order['tickets'][ticket_id].copy()
                del self.order['tickets'][ticket_id]
                self.order['tickets_count'] -= 1
                self.order['total'] -= self.decimal_price(ticket['price'])
                del ticket

            self.get_overall()

            # Обновление кэша заказа
            self.update_order()

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

    def change_order_type(self, customer, order_type):
        # Обновление типа получения и типа оплаты билетов
        self.order['delivery'] = ORDER_TYPE_MAPPING[order_type]['delivery']
        self.order['payment'] = ORDER_TYPE_MAPPING[order_type]['payment']

        # Обновление реквизитов покупателя
        self.order['customer']['name'] = customer['name']
        self.order['customer']['phone'] = customer['phone']
        self.order['customer']['email'] = customer['email']
        self.order['customer']['address'] = customer['address'] if self.order['delivery'] == 'courier' else None
        self.order['customer']['order_type'] = order_type

        # Информация о событии
        event = cache_factory('event', self.order['event_uuid'])
        # Информация о сервисе продажи билетов
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        # Информация о сервисе онлайн-оплаты
        payment_service = cache_factory('payment_service', event['payment_service_id'])

        # Процент сервисного сбора на каждый из билетов в заказе
        self.order['extra'] = (
            event['settings']['extra'][order_type] if
            'extra' in event['settings'] and order_type in event['settings']['extra'] else
            0
        )
        # Стоимость доставки курьером, если она используется
        self.order['courier_price'] = self.decimal_price(
            ticket_service['settings']['courier_price'] if self.order['delivery'] == 'courier' else 0
        )
        # Процент комиссии сервиса онлайн-оплаты, если он используется
        self.order['commission'] = self.decimal_price(
            payment_service['settings']['init']['commission'] if payment_service else 0
        )

        self.get_overall()

        # Обновление кэша заказа
        self.update_order()

    def get_overall(self):
        """Получение общей суммы заказа и её подписи в зависимости от возможных наценок/скидок."""

        # При доставке курьером - с учётом стоимости доставки курьером (если она задана)
        if self.order['delivery'] == 'courier':
            # Общая сумма заказа (с учётом сервисного сбора и стоимости доставки курьером)
            self.order['overall'] = self.total_plus_courier_price()
            if self.order['courier_price'] > 0:
                self.order['overall_header'] = (
                    ORDER_OVERALL_CAPTION['overall_courier_extra'] if
                    self.order['extra'] > 0 else
                    ORDER_OVERALL_CAPTION['overall_courier']
                )

        # При онлайн-оплате - с учётом комиссии сервиса онлайн-оплаты (если она задана)
        if self.order['payment'] == 'online':
            # Общая сумма заказа (с учётом сервисного сбора и комиссии сервиса онлайн-оплаты)
            self.order['overall'] = self.total_plus_commission()
            if self.order['commission'] > 0:
                self.order['overall_header'] = (
                    ORDER_OVERALL_CAPTION['overall_commission_extra'] if
                    self.order['extra'] > 0 else
                    ORDER_OVERALL_CAPTION['overall_commission']
                )
            else:
                self.order['overall_header'] = (
                    ORDER_OVERALL_CAPTION['overall_commission_extra'] if
                    self.order['extra'] > 0 else
                    ORDER_OVERALL_CAPTION['overall_total']
                )

        # Для любого типа заказа без дополнительных условий -
        # с учётом сервисного сбора для каждого билета в заказе (если он задан)
        self.order['overall'] = self.total_plus_extra()
        self.order['overall_header'] = (
            ORDER_OVERALL_CAPTION['overall_extra'] if
            self.order['extra'] > 0 else
            ORDER_OVERALL_CAPTION['overall_total']
        )

    def total_plus_extra(self):
        """Общая сумма заказа с учётом сервисного сбора.

        Если процент сервисного сбора больше ``0``,
        то к сумме заказа добавляется указанный процент от цены каждого из билетов в заказе.
        Если процент сервисного сбора равен ``0``, мы получаем ту же самую сумму.

        Returns:
            Decimal: Общая сумма заказа ``overall``.
        """
        total_plus_extra = self.order['total']
        if self.order['extra'] > 0:
            for ticket_id in self.order['tickets']:
                ticket_price = self.order['tickets'][ticket_id]['price']
                total_plus_extra += ((self.decimal_price(ticket_price) * self.order['extra']) / self.decimal_price(100))
        return total_plus_extra

    def total_plus_courier_price(self):
        """Общая сумма заказа с учётом стоимости доставки курьером.

        Если стоимость доставки курьером больше ``0``, то она добавляется к сумме заказа.
        Если стоимость доставки курьером равна ``0``, мы получаем ту же самую сумму.

        Returns:
            Decimal: Общая сумма заказа ``overall``.
        """
        return self.order['total'] + self.order['courier_price']

    def total_plus_commission(self):
        """Общая сумма заказа при онлайн-оплате.

        Если комиссия сервиса онлайн-оплаты не равна ``0``,
        то к сумме заказа добавляется указанный процент от самой суммы заказа.
        Если комиссия равна ``0``, мы получаем ту же самую сумму.

        Returns:
            Decimal: Общая сумма заказа ``overall``.
        """
        return self.order['total'] + ((self.order['total'] * self.order['commission']) / self.decimal_price(100))
        # return self.order['total'] + (self.order['total'] * (self.order['commission'] / self.decimal_price(100)))

    def decimal_price(self, value):
        """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа ``Decimal``.

        Args:
            value (str): Входное значение (в любом случае строка - для обхода проблем с округлением ``float``).

        Returns:
            Decimal: Денежная сумма.
        """
        return Decimal(str(value)).quantize(Decimal('1.00'))

    def now(self):
        return timezone_now().astimezone(
            pytz.timezone(self.order['city_timezone'])
        )
