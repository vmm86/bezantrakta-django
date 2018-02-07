import uuid
from decimal import Decimal

from django.db.models import F

from project.cache import ProjectCache

from ..models import Order, OrderTicket


class OrderCache(ProjectCache):
    entities = ('order', )
    # database_first = False

    def get_object(self, object_id, **kwargs):
        # pass
        try:
            # Получение информации о заказе
            order = Order.objects.annotate(
                event_uuid=F('event'),
                event_id=F('ticket_service_event'),
                order_uuid=F('id'),
                order_id=F('ticket_service_order'),
                overall=F('total'),
            ).values(
                'event_uuid',
                'event_id',
                'order_uuid',
                'order_id',
                'ticket_service_id',
                'name',
                'email',
                'phone',
                'delivery',
                'payment',
                'payment_id',
                'status',
                'tickets_count',
                'total',
                'overall'
            ).get(
                id=object_id,
            )
        except Order.DoesNotExist:
            pass
        else:
            # Получение билетов в заказе
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
                    'price_group_id',
                    'price'
                ).filter(
                    order_id=object_id
                ))
            except OrderTicket.DoesNotExist:
                order['tickets'] = []

            return order

    def cache_preprocessing(self, **kwargs):
        pass

    def cache_postprocessing(self, **kwargs):
        # Преобразование типов при получении заказа, если он непустой
        if self.value:
            for t in self.value['tickets']:
                t['ticket_uuid'] = uuid.UUID(t['ticket_uuid'])
                t['price'] = self.decimal_price(t['price'])

            self.value['total'] = self.decimal_price(self.value['total'])
            self.value['overall'] = self.decimal_price(self.value['overall'])

    def decimal_price(self, value):
        """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа ``Decimal``.

        Args:
            value (str): Входное значение (в любом случае строка - для обхода проблем с округлением ``float``).

        Returns:
            Decimal: Денежная сумма.
        """
        return Decimal(str(value)).quantize(Decimal('1.00'))
