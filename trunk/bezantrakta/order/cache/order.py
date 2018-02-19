from dateutil.parser import parse

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
            order = dict(Order.objects.annotate(
                event_uuid=F('event'),
                event_id=F('ticket_service_event'),
                order_uuid=F('id'),
                order_id=F('ticket_service_order'),
                updated=F('datetime'),
            ).values(
                'event_uuid',
                'event_id',
                'order_uuid',
                'order_id',
                'name',
                'email',
                'phone',
                'address',
                'delivery',
                'payment',
                'payment_id',
                'status',
                'tickets_count',
                'total',
                'overall',
                'updated'
            ).get(
                id=object_id,
            ))
        except Order.DoesNotExist:
            pass
        else:
            # Получение реквизитов покупателя
            order['customer'] = {}
            order['customer']['name'] = order.pop('name')
            order['customer']['phone'] = order.pop('phone')
            order['customer']['email'] = order.pop('email')
            order['customer']['address'] = order.pop('address')
            order['customer']['order_type'] = '{}_{}'.format(order['delivery'], order['payment'])

            # Получение билетов в заказе
            try:
                order['tickets'] = list(OrderTicket.objects.annotate(
                    ticket_uuid=F('id'),
                ).values(
                    'ticket_uuid',
                    'ticket_id',
                    'is_fixed',
                    'bar_code',
                    'sector_id',
                    'sector_title',
                    'row_id',
                    'seat_id',
                    'seat_title',
                    'price'
                ).filter(
                    order_id=object_id
                ))
            except OrderTicket.DoesNotExist:
                order['tickets'] = {}
            else:
                # Преобразование списка билетов к словарю из словарей, ключи которго - ``ticket_id``
                order['tickets'] = {t['ticket_id']: t for t in order['tickets']}

            print('from database!')
            return order

    def cache_preprocessing(self, **kwargs):
        pass

    def cache_postprocessing(self, **kwargs):
        if 'updated' in self.value:
            self.value['updated'] = parse(self.value['updated'])

        # for t in self.value['tickets']:
        #     t['ticket_uuid'] = uuid.UUID(t['ticket_uuid'])
        #     t['price'] = self.decimal_price(t['price'])
