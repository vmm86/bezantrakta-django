import uuid

from django.db import models
from django.utils.translation import ugettext as _

from ckeditor.fields import RichTextField


class TicketServiceSchemeVenueBinderManager(models.Manager):
    def get_queryset(self):
        return super(TicketServiceSchemeVenueBinderManager, self).get_queryset().select_related(
            'ticket_service', 'event_venue'
        )


class TicketServiceSchemeVenueBinder(models.Model):
    """
    Связующая таблица схем залов из сервисов продажи билетов и собтвенно залов в БД, привязанных к определённому городу.
    """
    objects = TicketServiceSchemeVenueBinderManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    ticket_service = models.ForeignKey(
        'ticket_service.TicketService',
        on_delete=models.CASCADE,
        db_column='ticket_service_id',
        verbose_name=_('ticketserviceschemevenuebinder_ticket_service'),
    )
    ticket_service_scheme_id = models.PositiveIntegerField(
        verbose_name=_('ticketserviceschemevenuebinder_ticket_service_scheme'),
    )
    ticket_service_scheme_title = models.CharField(
        max_length=128,
        verbose_name=_('ticketserviceschemevenuebinder_ticket_service_scheme_title'),
    )
    event_venue = models.ForeignKey(
        'event.EventVenue',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_column='event_venue_id',
        verbose_name=_('ticketserviceschemevenuebinder_event_venue'),
    )
    scheme = RichTextField(
        default='',
        config_name='scheme',
        help_text=_('ticketserviceschemevenuebinder_scheme_help_text'),
        verbose_name=_('ticketserviceschemevenuebinder_scheme'),
    )

    class Meta:
        app_label = 'ticket_service'
        db_table = 'third_party_ticket_service_scheme_venue_binder'
        verbose_name = _('ticketserviceschemevenuebinder')
        verbose_name_plural = _('ticketserviceschemevenuebinders')
        ordering = ('ticket_service', 'ticket_service_scheme_id', 'event_venue',)
        unique_together = (
            ('ticket_service', 'ticket_service_scheme_id',),
        )

    def __str__(self):
        return 'Схема {scheme_id}: {scheme_title}'.format(
            scheme_title=self.ticket_service_scheme_title,
            scheme_id=self.ticket_service_scheme_id
        )
