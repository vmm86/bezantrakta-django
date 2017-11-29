from django.db import models
from django.utils.translation import ugettext as _


class PaymentService(models.Model):
    """
    Сервисы онлайн-оплаты.
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
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('paymentservice_slug'),
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
        default='{}',
        verbose_name=_('paymentservice_settings'),
    )

    class Meta:
        app_label = 'payment_service'
        db_table = 'bezantrakta_payment_service'
        verbose_name = _('paymentservice')
        verbose_name_plural = _('paymentservices')
        ordering = ('id', 'title',)

    def __str__(self):
        return self.title