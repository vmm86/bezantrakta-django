import uuid

from django.db import models
from django.utils.translation import ugettext as _


class EventContainer(models.Model):
    """
    Контейнеры для отображения событий на сайте.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=32,
        verbose_name=_('eventcontainer_title'),
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('eventcontainer_slug'),
    )
    MODE_BV = 'big_vertical'
    MODE_BH = 'big_horizontal'
    MODE_SV = 'small_vertical'
    MODE_SH = 'small_horizontal'
    MODE_CHOICES = (
        (MODE_BV, _('eventcontainer_mode_big_vertical')),
        (MODE_BH, _('eventcontainer_mode_big_horizontal')),
        (MODE_SV, _('eventcontainer_mode_small_vertical')),
        (MODE_SH, _('eventcontainer_mode_small_horizontal')),
    )
    mode = models.CharField(
        choices=MODE_CHOICES,
        default=MODE_SV,
        blank=False,
        max_length=16,
        db_index=True,
        verbose_name=_('eventcontainer_mode'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('eventcontainer_order'),
    )
    img_width = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_('eventcontainer_img_width'),
    )
    img_height = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_('eventcontainer_img_height'),
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_('eventcontainer_is_published'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_container'
        verbose_name = _('eventcontainer')
        verbose_name_plural = _('eventcontainers')
        ordering = ('order', 'is_published', 'title',)

    def __str__(self):
        return self.title
