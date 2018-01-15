from django.db import models
from django.utils.translation import ugettext as _

from project.decorators import default_json_settings

from ..settings import DOMAIN_SETTINGS_DEFAULT


@default_json_settings(DOMAIN_SETTINGS_DEFAULT)
def default_json_settings_callable():
    pass


class DomainManager(models.Manager):
    """Менеджер модели ``Domain``."""
    def get_queryset(self):
        return super(DomainManager, self).get_queryset().select_related('city')


class Domain(models.Model):
    """Сайты Безантракта, работающие в разных городах России.

    Attributes:
        objects (django.db.models.DomainManager): Менеджер модели.
        id (django.db.models.IntegerField): Идентификатор.
        title (django.db.models.CharField): Название.
        slug (django.db.models.SlugField): Псевдоним.
        is_published (django.db.models.BooleanField): Работает или НЕ работает ("ведутся технические работы").
        city (django.db.models.ForeignKey): Привязка к городу, в котором работает сайт.
        settings (django.db.models.TextField): Настройки в JSON.
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
    slug = models.SlugField(
        max_length=8,
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
        default=default_json_settings_callable,
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
