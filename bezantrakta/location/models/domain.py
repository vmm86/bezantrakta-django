import simplejson as json
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


def get_default_domain_settings():
    """Получение настроек сайта по умолчанию из файла JSON."""
    domain_settings_file = os.path.join(
        settings.BASE_DIR,
        'bezantrakta',
        'location',
        'domain_settings.json',
    )
    with open(domain_settings_file, 'r') as dsf:
        return json.dumps(json.load(dsf), ensure_ascii=False)


class DomainManager(models.Manager):
    def get_queryset(self):
        return super(DomainManager, self).get_queryset().select_related('city')


class Domain(models.Model):
    """Сайты Безантракта, работающие в разных городах России.

    Attributes:
        objects (DomainManager): Менеджер модели.
        id (IntegerField): Идентификатор.
        title (CharField): Название.
        slug (CharField): Псевдоним (**TODO** - изменить на ``SlugField``).
        is_published (BooleanField): Работает (``True``) или не работает ("ведутся технические работы") (``False``).
        city (ForeignKey): Привязка к городу, в котором работает сайт.
        settings (TextField): Настройки в JSON.
    """
    objects = DomainManager()

    id = models.IntegerField(
        primary_key=True,
        help_text=_('domain_id_help_text'),
        verbose_name=_('domain_id'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('domain_title'),
    )
    slug = models.CharField(
        max_length=32,
        unique=True,
        help_text=_('domain_slug_help_text'),
        verbose_name=_('domain_slug'),
    )
    is_published = models.BooleanField(
        default=False,
        help_text=_('domain_is_published_help_text'),
        verbose_name=_('domain_is_published'),
    )
    city = models.ForeignKey(
        'location.City',
        on_delete=models.CASCADE,
        db_column='city_id',
        verbose_name=_('domain_city'),
    )
    settings = models.TextField(
        default=get_default_domain_settings,
        verbose_name=_('domain_settings'),
    )

    class Meta:
        app_label = 'location'
        db_table = 'bezantrakta_location_domain'
        verbose_name = _('domain')
        verbose_name_plural = _('domains')
        ordering = ('city', 'title',)

    def __str__(self):
        return '{title} - {slug}'.format(title=self.title, slug=self.slug)
