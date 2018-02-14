import uuid
from decimal import Decimal

from bezantrakta.order.settings import ORDER_OVERALL_CAPTION

from project.cache import cache_factory


class OrderBasket():
    """Класс для работы с предварительными резервами и созданными заказами.

    Проводит определённые операции с заказом, получая информацию о нём из кэша.

    Attributes:
        order (dict): Параметры текущего предварительного резерва или созданного заказа.
            Содержимое ``order``:
                * order_uuid (uuid.UUID): UUID заказа.
                * order_id (int): Идентификатор заказа (после его успешного создания и записи в БД), иначе ``None``.

                * event_uuid (uuid.UUID): UUID события.
                * event_id (int): Идентификатор события.

                * ticket_service_id (str): Идентификатор сервиса продажи билетов.

                * customer_name (str): ФИО покупателя.
                * customer_phone (str): Телефон покупателя.
                * customer_email (str): Электронная почта покупателя.
                * customer_address (str): Адрес доставки (если она нужна), иначе ``None``. ???

                * order_type (str): Тип заказа билетов ("способ получения"_"способ оплаты").
                    Возможные значения ``order_type``:
                        * self_online:
                        * email_online:
                        * self_cash:
                        * courier_cash:
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
        # Получение существующего или создание нового пустого предварительного резерва
        if 'order_uuid' in kwargs and kwargs['order_uuid']:
            self.get_order(kwargs['order_uuid'])
        else:
            self.order = {}

            self.order['order_uuid'] = uuid.uuid4()

            self.order['order_id'] = None

            self.order['event_uuid'] = (
                kwargs['event_uuid'] if
                'event_uuid' in kwargs else
                None
            )

            self.order['event_id'] = (
                kwargs['event_id'] if
                'event_id' in kwargs else
                None
            )

            self.order['ticket_service_id'] = (
                kwargs['ticket_service_id'] if
                'ticket_service_id' in kwargs else
                None
            )

            self.order['customer_name'] = None
            self.order['customer_phone'] = None
            self.order['customer_email'] = None

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
        self.order = cache_factory('order', self.order['order_uuid'], obj=self.order, reset=True)

    def delete_order(self):
        # Полностью удалить существующий заказ
        cache_factory('order', self.order['order_uuid'], delete=True)

    def add_ticket(self, ticket):
        ticket_id = ticket['ticket_id']
        t = {
            'ticket_uuid':    ticket['ticket_uuid'],
            'sector_id':      ticket['sector_id'],
            'sector_title':   ticket['sector_title'],
            'row_id':         ticket['row_id'],
            'seat_id':        ticket['seat_id'],
            'seat_title':     ticket['seat_title'],
            'price':          self.decimal_price(ticket['price']),
            'price_order':    ticket['price_order'],
            'added':          ticket['added'],
        }
        self.order['tickets'][ticket_id] = t
        self.order['tickets_count'] += 1
        self.order['total'] += self.decimal_price(ticket['price'])

        self.order['overall'] = self.get_overall()

        # Обновление кэша заказа
        self.update_order()

    def remove_ticket(self, ticket_id):
        ticket = self.order['tickets'][ticket_id].copy()
        del self.order['tickets'][ticket_id]
        self.order['tickets_count'] -= 1
        self.order['total'] -= self.decimal_price(ticket['price'])
        del ticket

        self.order['overall'] = self.get_overall()

        # Обновление кэша заказа
        self.update_order()

    def decimal_price(self, value):
        """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа ``Decimal``.

        Args:
            value (str): Входное значение (в любом случае строка - для обхода проблем с округлением ``float``).

        Returns:
            Decimal: Денежная сумма.
        """
        return Decimal(str(value)).quantize(Decimal('1.00'))

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
            for ticket in self.order.tickets:
                total_plus_extra += ((self.decimal_price(ticket['price']) * self.order['extra']) / 100)
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
