from django.db import models
from django.utils.translation import ugettext as _

from project.decorators import default_json_settings

from ..settings import PAYMENT_SERVICE_SETTINGS_DEFAULT


@default_json_settings(PAYMENT_SERVICE_SETTINGS_DEFAULT)
def default_json_settings_callable():
    """Получение JSON-настроек по умолчанию."""
    pass


class PaymentService(models.Model):
    """Сервисы онлайн-оплаты.

    Attributes:
        id (SlugField): Идентификатор.
        title (CharField): Название.
        slug (SlugField): Псевдоним (должен совпадать с атрибутом ``slug`` класса сервиса-онлайн-оплаты).
        is_active (BooleanField): Работает (``True``) или НЕ работает (``False``).
        is_production (BooleanField): Оплата настоящими деньгами (``True``) или тестовая оплата (``False``).
        settings (TextField): Настройки сервиса-онлайн-оплаты в *JSON*.
    """
    id = models.SlugField(
        primary_key=True,
        editable=True,
        max_length=32,
        verbose_name=_('paymentservice_id'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('paymentservice_title'),
    )
    SLUG_SBERBANK = 'sberbank'
    SLUG_SNGB = 'sngb'
    SLUG_CHOICES = (
        (SLUG_SBERBANK, _('paymentservice_slug_sberbank')),
        (SLUG_SNGB, _('paymentservice_slug_sngb')),
    )
    slug = models.CharField(
        choices=SLUG_CHOICES,
        blank=False,
        max_length=32,
        verbose_name=_('paymentservice_slug')
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('paymentservice_is_active'),
    )
    is_production = models.BooleanField(
        default=False,
        help_text=_('paymentservice_is_production_help_text'),
        verbose_name=_('paymentservice_is_production'),
    )
    settings = models.TextField(
        default=default_json_settings_callable,
        verbose_name=_('paymentservice_settings'),
    )

    class Meta:
        app_label = 'payment_service'
        db_table = 'third_party_payment_service'
        verbose_name = _('paymentservice')
        verbose_name_plural = _('paymentservices')
        ordering = ('slug', 'title',)

    def __str__(self):
        return self.title
