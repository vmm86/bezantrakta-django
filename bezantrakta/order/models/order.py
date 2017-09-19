import uuid

from django.db import models
from django.urls.base import reverse
from django.utils.translation import ugettext as _

from phonenumber_field.modelfields import PhoneNumberField


class OrderManager(models.Manager):
    def get_queryset(self):
        return super(OrderManager, self).get_queryset().select_related(
            'ticket_service', 'event', 'domain'
        )


class Order(models.Model):
    """Заказы в сторонних сервисах продажи билетов."""
    objects = OrderManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    ticket_service = models.ForeignKey(
        'ticket_service.TicketService',
        on_delete=models.CASCADE,
        db_column='ticket_service_id',
        verbose_name=_('order_ticket_service'),
    )
    ticket_service_order = models.PositiveIntegerField(
        blank=True,
        null=True,
        db_column='ticket_service_order_id',
        verbose_name=_('order_ticket_service_order'),
    )
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        db_column='event_id',
        verbose_name=_('order_event'),
    )
    ticket_service_event = models.PositiveIntegerField(
        db_column='ticket_service_event_id',
        verbose_name=_('order_ticket_service_event'),
    )
    datetime = models.DateTimeField(
        verbose_name=_('order_datetime'),
    )
    name = models.CharField(
        max_length=128,
        verbose_name=_('order_name'),
    )
    email = models.EmailField(
        verbose_name=_('order_email'),
    )
    phone = PhoneNumberField(
        max_length=20,
        verbose_name=_('order_phone'),
    )
    address = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_('order_address'),
    )
    # delivery | payment
    # ---------|---------
    # self     | cash
    # courier  | cash
    # self     | online
    # email    | online
    DELIVERY_SELF = 'self'
    DELIVERY_COURIER = 'courier'
    DELIVERY_EMAIL = 'email'
    DELIVERY_CHOICES = (
        (DELIVERY_SELF, _('order_mode_self')),
        (DELIVERY_COURIER, _('order_mode_courier')),
        (DELIVERY_EMAIL, _('order_mode_email')),
    )
    delivery = models.CharField(
        max_length=16,
        choices=DELIVERY_CHOICES,
        default=DELIVERY_SELF,
        blank=False,
        verbose_name=_('order_delivery'),
    )
    MODE_CASH = 'cash'
    MODE_ONLINE = 'online'
    MODE_CHOICES = (
        (MODE_CASH, _('order_mode_cash')),
        (MODE_ONLINE, _('order_mode_online')),
    )
    payment = models.CharField(
        max_length=16,
        choices=MODE_CHOICES,
        default=MODE_CASH,
        blank=False,
        verbose_name=_('order_payment'),
    )
    payment_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name=_('order_payment_id'),
    )
    # STATUS_RESERVED = 'reserved'  # Статус предварительно зарезервированных мест, когда заказ ещё не создан
    STATUS_ORDERED = 'ordered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_APPROVED = 'approved'
    STATUS_REFUNDED = 'refunded'
    STATUS_CHOICES = (
        (STATUS_ORDERED, _('order_status_ordered')),
        (STATUS_CANCELLED, _('order_status_cancelled')),
        (STATUS_APPROVED, _('order_status_approved')),
        (STATUS_REFUNDED, _('order_status_refunded')),
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_ORDERED,
        blank=False,
        verbose_name=_('order_status'),
    )
    tickets_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('order_tickets_count'),
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('order_total'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('order_domain'),
    )

    class Meta:
        app_label = 'order'
        db_table = 'bezantrakta_order'
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ('domain', '-datetime', 'ticket_service',)
        unique_together = (
            ('domain', 'id',),
        )

    def __str__(self):
        return 'Заказ {order_uuid} ({tickets_count} билетов на {total} р.)'.format(
            order_uuid=self.id,
            tickets_count=self.tickets_count,
            total=self.total,
        )

    def get_absolute_url(self):
        return reverse(
            'order',
            args=[
                str(self.id),
            ]
        )
