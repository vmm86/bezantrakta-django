from django.db import models
from django.utils.translation import ugettext as _

from project.decorators import default_json_settings

from ..settings import TICKET_SERVICE_SETTINGS_DEFAULT


@default_json_settings(TICKET_SERVICE_SETTINGS_DEFAULT)
def default_json_settings_callable():
    """Получение JSON-настроек по умолчанию."""
    pass


class TicketServiceManager(models.Manager):
    """Менеджер модели ``TicketServiceManager``."""
    def get_queryset(self):
        return super(TicketServiceManager, self).get_queryset().select_related(
            'domain', 'payment_service'
        ).prefetch_related(
            'schemes'
        )


class TicketService(models.Model):
    """Сервисы продажи билетов.

    Attributes:
        objects (TicketServiceManager): Менеджер модели.
        id (SlugField): Идентификатор.
        title (CharField): Название.
        slug (SlugField): Псевдоним (должен совпадать с атрибутом ``slug`` класса сервиса-онлайн-оплаты).
        is_active (BooleanField): Работает (``True``) или НЕ работает (``False``).
        settings (TextField): Настройки в JSON.
        domain (ForeignKey): Сайт, к которому привязан сервис продажи билетов.
        schemes (ManyToManyField): Связь со схемами залов, импорируемыми из стороннего сервиса продажи билетов в БД.
        payment_service (ForeignKey): Сервис онлайн-оплаты (может отсутствовать).
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
    SLUG_SUPERBILET = 'superbilet'
    SLUG_RADARIO = 'radario'
    SLUG_CHOICES = (
        (SLUG_SUPERBILET, _('ticketservice_slug_superbilet')),
        (SLUG_RADARIO, _('ticketservice_slug_radario')),
    )
    slug = models.CharField(
        choices=SLUG_CHOICES,
        blank=False,
        max_length=32,
        verbose_name=_('ticketservice_slug')
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('ticketservice_is_active'),
    )
    settings = models.TextField(
        default=default_json_settings_callable,
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
