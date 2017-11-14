import uuid

from django.db import models
from django.utils.translation import ugettext as _


class EventGroupBinderManager(models.Manager):
    def get_queryset(self):
        return super(EventGroupBinderManager, self).get_queryset().select_related('group', 'event')


class EventGroupBinder(models.Model):
    """Связующая таблица событий и групп событий.

    Attributes:
        objects (EventGroupBinderManager): Менеджер модели.
        id (UUIDField): Уникальный идентификатор.
        group (ForeignKey): Привязка к группе, которая содержит события.
        event (ForeignKey): Привязка к событиям, которые входят в группу.
        caption (CharField): Опциональная подпись к событию в группе.
    """
    objects = EventGroupBinderManager()

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
        ordering = ('group__datetime', '-event__datetime', 'caption',)
        unique_together = (
            ('group', 'event',),
        )

    def __str__(self):
        return '{event} 🔗 {group}'.format(
            event=self.event,
            group=self.group
        )
