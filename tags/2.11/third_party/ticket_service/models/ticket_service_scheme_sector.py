import uuid

from django.db import models
from django.utils.translation import ugettext as _

from ckeditor.fields import RichTextField


class TicketServiceSchemeSectorManager(models.Manager):
    def get_queryset(self):
        return super(TicketServiceSchemeSectorManager, self).get_queryset().select_related(
            'scheme'
        )


class TicketServiceSchemeSector(models.Model):
    """Опциональные секторы, на которые при необходимости для удобства можно разбить слишком большую схему зала.

    Attributes:
        objects (TicketServiceSchemeSectorsManager): Менеджер модели.
        id (UUIDField): Идентифкатор.
        scheme (ForeignKey): Схема зала, импортированная из сервиса продажи билетов, к которой добавляется сектор.
        ticket_service_sector_id (PositiveIntegerField): Идентификатор сектора.
        ticket_service_sector_title (CharField): Название сектора.
        sector (RichTextField): Схема сектора в HTML или SVG.
    """
    objects = TicketServiceSchemeSectorManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    scheme = models.ForeignKey(
        'ticket_service.TicketServiceSchemeVenueBinder',
        related_name='scheme_sectors',
        on_delete=models.CASCADE,
        db_column='ticket_service_scheme_id',
        verbose_name=_('ticketserviceschemesector_scheme'),
    )
    ticket_service_sector_id = models.PositiveIntegerField(
        verbose_name=_('ticketserviceschemesector_ticket_service_sector_id'),
    )
    ticket_service_sector_title = models.CharField(
        max_length=128,
        verbose_name=_('ticketserviceschemesector_ticket_service_sector_title'),
    )
    sector = RichTextField(
        default='',
        config_name='scheme',
        help_text=_('ticketserviceschemesector_sector_help_text'),
        verbose_name=_('ticketserviceschemesector_sector'),
    )

    class Meta:
        app_label = 'ticket_service'
        db_table = 'third_party_ticket_service_scheme_sector'
        verbose_name = _('ticketserviceschemesector')
        verbose_name_plural = _('ticketserviceschemesectors')
        ordering = ('scheme', 'ticket_service_sector_id',)
        unique_together = (
            ('scheme', 'ticket_service_sector_id',),
        )

    def __str__(self):
        return 'Сектор {sector_id}: {sector_title} в схеме {scheme_id}: {scheme_title}'.format(
            sector_id=self.ticket_service_sector_id,
            sector_title=self.ticket_service_sector_title,
            scheme_id=self.scheme.ticket_service_scheme_id,
            scheme_title=self.scheme.ticket_service_scheme_title,
        )
