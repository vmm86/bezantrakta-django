import uuid

from django.db import models
from django.utils.translation import ugettext as _


class OrderTicketManager(models.Manager):
    def get_queryset(self):
        return super(OrderTicketManager, self).get_queryset().select_related(
            'order', 'ticket_service', 'domain'
        )


class OrderTicket(models.Model):
    """Билеты в заказах из сторонних сервисов продажи билетов."""
    objects = OrderTicketManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('order_ticket_id'),
    )
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.CASCADE,
        db_column='order_id',
        verbose_name=_('order_ticket_order'),
    )
    ticket_service = models.ForeignKey(
        'ticket_service.TicketService',
        on_delete=models.CASCADE,
        db_column='ticket_service_id',
        verbose_name=_('order_ticket_ticket_service'),
    )
    ticket_service_order = models.PositiveIntegerField(
        null=True,
        db_column='ticket_service_order_id',
        verbose_name=_('order_ticket_ticket_service_order'),
    )
    is_punched = models.BooleanField(
        default=False,
        verbose_name=_('order_ticket_is_punched'),
    )
    bar_code = models.CharField(
        null=True,
        max_length=32,
        verbose_name=_('order_ticket_bar_code'),
    )
    sector_id = models.PositiveIntegerField(
        null=True,
        verbose_name=_('order_ticket_sector'),
    )
    sector_title = models.CharField(
        null=True,
        max_length=128,
        verbose_name=_('order_ticket_sector_title'),
    )
    row_id = models.PositiveIntegerField(
        null=True,
        verbose_name=_('order_ticket_row'),
    )
    seat_id = models.PositiveIntegerField(
        null=True,
        verbose_name=_('order_ticket_seat'),
    )
    seat_title = models.CharField(
        null=True,
        max_length=128,
        verbose_name=_('order_ticket_seat_title'),
    )
    price_group_id = models.PositiveIntegerField(
        null=True,
        verbose_name=_('order_ticket_price_group'),
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('order_ticket_price'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('order_ticket_domain'),
    )

    class Meta:
        app_label = 'order'
        db_table = 'bezantrakta_order_ticket'
        verbose_name = _('order_ticket')
        verbose_name_plural = _('order_tickets')
        ordering = ('domain', 'ticket_service', '-ticket_service_order',
                    'sector_id', 'row_id', 'seat_id', 'price',)
        unique_together = (
            ('domain', 'sector_id', 'row_id', 'seat_id', 'price_group_id',),
        )

    def __str__(self):
        return 'Билет {ticket_uuid} из заказа {order_uuid}'.format(
            ticket_uuid=self.id,
            order_uuid=self.ticket_service_order,
        )
