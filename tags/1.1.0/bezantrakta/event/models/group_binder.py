import uuid

from django.db import models
from django.utils.translation import ugettext as _


class EventGroupBinder(models.Model):
    """
    Связующая таблица событий и групп событий.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    group = models.ForeignKey(
        'event.Event',
        related_name='groups',
        on_delete=models.CASCADE,
        db_column='group_id',
        verbose_name=_('eventgroupbinder_event_group'),
    )
    event = models.ForeignKey(
        'event.Event',
        related_name='events',
        on_delete=models.CASCADE,
        db_column='event_id',
        verbose_name=_('eventgroupbinder_event'),
    )
    caption = models.CharField(
        max_length=64,
        blank=True,
        help_text=_('eventgroupbinder_title_help_text'),
        verbose_name=_('eventgroupbinder_title'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_group_binder'
        verbose_name = _('eventgroupbinder')
        verbose_name_plural = _('eventgroupbinders')
        ordering = ('group__datetime', 'event__datetime', 'caption',)

    def __str__(self):
        return ''
