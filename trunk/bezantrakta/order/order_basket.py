import uuid

from decimal import Decimal

from project.cache import cache_factory
from project.shortcuts import timezone_now


class OrderBasket():
    """Класс для работы с заказами.

       Проводит определённые операции с заказом, получая информацию о нём из кэша заказа.
    """
    # event_uuid (uuid.UUID)
    # event_id (int)
    # order_uuid (uuid.UUID)
    # order_id (int)
    # ticket_service_id (str)

    # customer_name (str)
    # customer_phone (str)
    # customer_email (str)

    # delivery (str) self | courier | email
    # payment (str) cash | online
    # payment_id (str) or None

    # status (str) reserved | ordered | approved | cancelled | refunded

    # tickets (list)
    # |- ticket_uuid (uuid.UUID)
    # |- sector_id (int)
    # |- sector_title (str)
    # |- row_id (int)
    # |- seat_id (int)
    # |- seat_title (str)
    # |- price_group_id (int)
    # |- bar_code (str)

    # tickets_count (int)
    # total (decimal.Decimal)
    # overall (decimal.Decimal)

    def __init__(self, **kwargs):
        self.order = cache_factory('order', kwargs['order_uuid'])

        # Создание нового пустого заказа при его отсутствии
        if not self.order:
            self.order = {}

            self.order['order_uuid'] = kwargs['order_uuid']
            # self.order['order_id'] = None

            self.order['event_uuid'] = (
                kwargs['event_uuid'] if
                'event_uuid' in kwargs else
                None
            )

            self.order['event_service_id'] = (
                kwargs['event_service_id'] if
                'event_service_id' in kwargs else
                None
            )

            self.order['ticket_service_id'] = (
                kwargs['ticket_service_id'] if
                'ticket_service_id' in kwargs else
                None
            )

            # self.order['customer_name'] = ''
            # self.order['customer_phone'] = ''
            # self.order['customer_email'] = ''

            # self.order['delivery'] = ''
            # self.order['payment'] = ''
            # self.order['payment_id'] = None

            self.order['status'] = 'reserved'

            self.order['tickets'] = []
            self.order['tickets_count'] = 0
            self.order['total'] = self.decimal_price(0)
            self.order['overall'] = self.decimal_price(0)

            # Создание кэша нового заказа
            cache_factory('order', self.order['order_uuid'], obj=self.order, reset=True)

    def __str__(self):
        return '{cls}({order_uuid})'.format(
            cls=self.__class__.__name__,
            order_uuid=self.order['order_uuid'],
        )

    def add_ticket(self, ticket):
        t = {
            'ticket_uuid':    uuid.uuid4(),
            'sector_id':      ticket['sector_id'],
            'sector_title':   ticket['sector_title'],
            'row_id':         ticket['row_id'],
            'seat_id':        ticket['seat_id'],
            'seat_title':     ticket['seat_title'],
            'price_group_id': ticket['price_group_id'],
            'price':          self.decimal_price(ticket['price']),
            'price_order':    ticket['price_order'],
        }
        self.order['tickets'].append(t)
        self.order['tickets_count'] += 1
        self.order['total'] += self.decimal_price(ticket['price'])

        self.order['overall'] = self.order['total']

        # Обновление кэша заказа
        cache_factory('order', self.order['order_uuid'], obj=self.order, reset=True)

    def remove_ticket(self, ticket):
        self.order['tickets'][:] = [t for t in self.order['tickets'] if not (t['sector_id'] == ticket['sector_id'] and t['row_id'] == ticket['row_id'] and t['seat_id'] == ticket['seat_id'])]
        self.order['tickets_count'] -= 1
        self.order['total'] -= self.decimal_price(ticket['price'])

        self.order['overall'] = self.order['total']

        # Обновление кэша заказа
        cache_factory('order', self.order['order_uuid'], obj=self.order, reset=True)

    def delete_order_cache(self):
        # Удалить кэш заказа
        cache_factory('order', self.order['order_uuid'], delete=True)

    def decimal_price(self, value):
        """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа ``Decimal``.

        Args:
            value (str): Входное значение (в любом случае строка - для обхода проблем с округлением ``float``).

        Returns:
            Decimal: Денежная сумма.
        """
        return Decimal(str(value)).quantize(Decimal('1.00'))

    def total_plus_extra(self, extra):
        """Общая сумма заказа с учётом сервисного сбора.

        Если процент сервисного сбора ``extra`` больше ``0``,
        то к общей сумме заказа добавляется указанный процент от цены каждого из билетов в заказе.
        Если процент сервисного сбора равен ``0``, т.е. не используется, мы получаем ту же самую сумму.

        Args:
            extra (Decimal): Процент сервисного сбора.
        """
        total_plus_extra = self.order.total
        if extra > 0:
            for ticket in self.order.tickets:
                total_plus_extra += ((self.decimal_price(ticket['price']) * extra) / 100)
        return total_plus_extra

    def total_plus_courier_price(self, courier_price):
        """Общая сумма заказа с учётом стоимости доставки курьером.

        Стоимость доставки курьером добавляется к сумме заказа, если она не равна 0.
        Если стоимость доставки курьером равна ``0``, т.е. бесплатна, мы получаем ту же самую сумму.

        Args:
            courier_price (Decimal): Стоимость доставки курьером.

        Returns:
            Decimal: Общая сумма заказа.
        """
        return self.order.total + courier_price

    def total_plus_commission(self, commission):
        """Общая сумма заказа при онлайн-оплате.

        Комиссия сервиса онлайн-оплаты добавляется к сумме заказа, если она не равна 0.
        Если комиссия равна ``0``, т.е. не используется, мы получаем ту же самую сумму.

        Returns:
            Decimal: Общая сумма заказа.
        """
        return self.decimal_price(self.order.total + ((self.order.total * commission) / self.decimal_price(100)))

    def get_overall(self, tickets, total, extra, courier_price, commission):
        """Получение общей суммы заказа в зависимости от возможных наценок/скидок."""

        # Для любого типа заказа - с учётом сервисного сбора для каждого билета в заказе (если он задан)
        self.overall = self.order.total_plus_extra(self.order.tickets, self.order.total, extra)

        # При доставке курьером - с учётом стоимости доставки курьером (если она задана)
        if self.delivery == 'courier':
            # Общая сумма заказа (с учётом сервисного сбора и стоимости доставки курьером)
            self.overall = self.order.total_plus_courier_price(self.overall, courier_price)

        # При онлайн-оплате - с учётом комиссии сервиса онлайн-оплаты (если она задана)
        if self.payment == 'online':
            # Общая сумма заказа (с учётом сервисного сбора и комиссии сервиса онлайн-оплаты)
            self.overall = self.order.total_plus_commission(self.overall, commission)
