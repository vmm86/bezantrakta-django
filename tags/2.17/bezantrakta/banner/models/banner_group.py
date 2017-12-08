import uuid

from django.db import models
from django.utils.translation import ugettext as _


class BannerGroup(models.Model):
    """Группы баннеров для показа в разных блоках в шаблоне сайта.

    Attributes:
        id (UUIDField): Уникальный идентификатор.
        title (CharField): Название.
        slug (SlugField): Псевдоним.
        order (PositiveSmallIntegerField): Порядок групп в админ-панели.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=32,
        verbose_name=_('bannergroup_title'),
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('bannergroup_slug'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        null=False,
        verbose_name=_('bannergroup_order'),
    )

    class Meta(object):
        app_label = 'banner'
        db_table = 'bezantrakta_banner_group'
        verbose_name = _('bannergroup')
        verbose_name_plural = _('bannergroups')
        ordering = ('order', 'title',)

    def __str__(self):
        return self.title
