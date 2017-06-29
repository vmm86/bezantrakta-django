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
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        db_column='event_id',
        verbose_name=_('eventgroupbinder_event'),
    )
    event_group = models.ForeignKey(
        'event.EventGroup',
        on_delete=models.CASCADE,
        db_column='event_group_id',
        verbose_name=_('eventgroupbinder_event_group'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_group_binder'
        verbose_name = _('eventgroupbinder')
        verbose_name_plural = _('eventgroupbinders')
        ordering = ('event_group', 'event',)

    def __str__(self):
        return '{group} <-> {event}'.format(group=self.event_group, event=self.event)
