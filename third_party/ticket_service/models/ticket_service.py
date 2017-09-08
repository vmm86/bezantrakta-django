from django.db import models
from django.utils.translation import ugettext as _


class TicketServiceManager(models.Manager):
    def get_queryset(self):
        return super(TicketServiceManager, self).get_queryset().select_related(
            'domain', 'payment_service'
        ).prefetch_related(
            'schemes'
        )


class TicketService(models.Model):
    """
    Сервисы продажи билетов.
    """
    objects = TicketServiceManager()

    id = models.SlugField(
        primary_key=True,
        editable=True,
        max_length=32,
        verbose_name=_('ticketservice_id'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('ticketservice_title'),
    )
    slug = models.SlugField(
        max_length=32,
        help_text=_('ticketservice_slug_help_text'),
        verbose_name=_('ticketservice_slug'),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('ticketservice_is_active'),
    )
    settings = models.TextField(
        default='{}',
        verbose_name=_('ticketservice_settings'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('ticketservice_domain'),
    )
    schemes = models.ManyToManyField(
        'event.EventVenue',
        through='ticket_service.TicketServiceSchemeVenueBinder',
        related_name='schemes',
        blank=True,
        verbose_name=_('ticketservice_schemes'),
    )
    payment_service = models.ForeignKey(
        'payment_service.PaymentService',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_column='payment_service_id',
        verbose_name=_('ticketservice_payment_service'),
    )

    class Meta:
        app_label = 'ticket_service'
        db_table = 'third_party_ticket_service'
        verbose_name = _('ticketservice')
        verbose_name_plural = _('ticketservices')
        ordering = ('slug', 'title',)

    def __str__(self):
        return self.title
