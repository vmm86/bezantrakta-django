from django.db import models
from django.utils.safestring import mark_safe


class EventLinkBinder(models.Model):
    """
    Связующая таблица событий и ссылок.
    """
    event = models.ForeignKey(
        'event.Event',
        on_delete=models.CASCADE,
        db_column='event_id',
        verbose_name='Событие',
    )
    event_link = models.ForeignKey(
        'event.EventLink',
        on_delete=models.CASCADE,
        db_column='event_link_id',
        verbose_name='Ссылки',
    )
    href = models.URLField(
        blank=True,
        verbose_name='Внешняя ссылка',
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Порядок',
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_link_binder'
        verbose_name = 'связь событий и ссылок'
        verbose_name_plural = 'связь событий и ссылок'
        ordering = ('order', 'event', 'event_link',)
        unique_together = (
            ('event', 'event_link',),
        )

    def __str__(self):
        return ''

    def img_preview(self):
        return mark_safe('<img src="{}" style="width: 200px; height: auto;">'.format(self.event_link.img.url))
    img_preview.short_description = 'Логотип'