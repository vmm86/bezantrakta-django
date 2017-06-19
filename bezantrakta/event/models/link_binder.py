import uuid

from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class EventLinkBinder(models.Model):
    """
    Связующая таблица событий и ссылок.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        db_column='event_id',
        verbose_name=_('eventlinkbunder_event'),
    )
    event_link = models.ForeignKey(
        'event.EventLink',
        on_delete=models.CASCADE,
        db_column='event_link_id',
        verbose_name=_('eventlinkbunder_event_link'),
    )
    href = models.URLField(
        blank=True,
        verbose_name=_('eventlinkbunder_href'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('eventlinkbunder_order'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_link_binder'
        verbose_name = _('eventlinkbunder')
        verbose_name_plural = _('eventlinkbunders')
        ordering = ('order', 'event', 'event_link',)
        unique_together = (
            ('event', 'event_link',),
        )

    def __str__(self):
        return ''

    def img_preview(self):
        return mark_safe('<img src="{}" style="width: 200px; height: auto;">'.format(self.event_link.img.url))
    img_preview.short_description = _('eventlinkbunder_img_preview')
