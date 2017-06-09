import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe


def img_path(instance, filename):
    if instance.event.domain is None:
        domain = 'global'
    else:
        domain = instance.event.domain.slug

    name, dot, extension = filename.rpartition('.')
    # Относительный путь до файла
    file_path = os.path.join(
        domain,
        instance._meta.app_label,
        ''.join(
            (instance.event.date.strftime('%Y-%m-%d'), '_', instance.event.slug,)
        ),
        ''.join(
            (instance.event_container.slug, dot, extension,)
        )
    )
    # Абсолютный путь до файла
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    # Если файл уже был загружен ранее,
    # удаляем его и сохраняем новый файл с таким же именем
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)

    return file_path


class EventContainerBinder(models.Model):
    """
    Связующая таблица событий и контейнеров событий.
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
    event_container = models.ForeignKey(
        'event.EventContainer',
        on_delete=models.CASCADE,
        db_column='event_container_id',
        verbose_name='Группа событий',
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Порядок в контейнере',
    )
    img = models.ImageField(
        upload_to=img_path,
        blank=True,
        null=True,
        verbose_name='Афиша'
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_container_binder'
        verbose_name = 'связь событий и контейнеров'
        verbose_name_plural = 'связь событий и контейнеров'
        ordering = ('order', 'event', 'event_container',)
        unique_together = (
            ('event', 'event_container', 'order',),
        )

    def __str__(self):
        return ''

    def delete(self, *args, **kwargs):
        full_file_path = os.path.join(settings.MEDIA_ROOT, str(self.img))
        if os.path.isfile(full_file_path):
            os.remove(full_file_path)

        super().delete(*args, **kwargs)

    def img_preview(self):
        return mark_safe(
            '<img src="{}" style="width: auto; height: 100px;">'.format(self.img.url)
        )
    img_preview.short_description = 'Афиша'

    def event_date(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        return mark_safe(
            '{}'.format(naturalday(self.event.date))
        )
    event_date.short_description = 'Дата'
