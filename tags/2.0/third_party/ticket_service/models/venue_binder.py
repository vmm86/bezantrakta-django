import uuid

from django.db import models
from django.utils.translation import ugettext as _

from ckeditor.fields import RichTextField


class TicketServiceVenueBinderManager(models.Manager):
    def get_queryset(self):
        return super(TicketServiceVenueBinderManager, self).get_queryset().select_related(
            'ticket_service', 'event_venue'
        )


class TicketServiceVenueBinder(models.Model):
    """
    Связующая таблица сервисов продажи билетов и залов на сайтах, для которых сервисы продажи билетов добавлены.
    """
    objects = TicketServiceVenueBinderManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    ticket_service = models.ForeignKey(
        'ticket_service.TicketService',
        on_delete=models.CASCADE,
        db_column='ticket_service_id',
        verbose_name=_('ticketservicevenuebinder_ticket_service'),
    )
    ticket_service_event_venue_id = models.PositiveIntegerField(
        verbose_name=_('ticketservicevenuebinder_ticket_service_event_venue'),
    )
    ticket_service_event_venue_title = models.CharField(
        max_length=128,
        verbose_name=_('ticketservicevenuebinder_ticket_service_event_venue_title'),
    )
    event_venue = models.ForeignKey(
        'event.EventVenue',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_column='event_venue_id',
        verbose_name=_('ticketservicevenuebinder_event_venue'),
    )
    scheme = RichTextField(
        default='',
        config_name='scheme',
        help_text=_('ticketservicevenuebinder_scheme_help_text'),
        verbose_name=_('ticketservicevenuebinder_scheme'),
    )

    class Meta:
        app_label = 'ticket_service'
        db_table = 'bezantrakta_ticket_service_venue_binder'
        verbose_name = _('ticketservicevenuebinder')
        verbose_name_plural = _('ticketservicevenuebinders')
        ordering = ('ticket_service', 'ticket_service_event_venue_id', 'event_venue',)
        unique_together = (
            ('ticket_service', 'ticket_service_event_venue_id',),
        )

    def __str__(self):
        return ''
