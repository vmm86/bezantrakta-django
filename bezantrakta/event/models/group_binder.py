import uuid

from django.db import models


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
        verbose_name='Событие',
    )
    event_group = models.ForeignKey(
        'event.EventGroup',
        on_delete=models.CASCADE,
        db_column='event_group_id',
        verbose_name='Группа событий',
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_group_binder'
        verbose_name = 'связка событий и групп событий'
        verbose_name_plural = 'связки событий и групп событий'

    def __str__(self):
        return ''
