import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


def img_path(instance, filename):
    if instance.event.domain is None:
        domain = 'global'
    else:
        domain = instance.event.domain.slug

    current_timezone = instance.event.domain.city.timezone
    event_datetime_localized = instance.event.datetime.astimezone(current_timezone)

    name, dot, extension = filename.rpartition('.')
    # Относительный путь до файла
    file_path = os.path.join(
        domain,
        instance._meta.app_label,
        ''.join(
            (
                event_datetime_localized.strftime('%Y-%m-%d'),
                '_',
                event_datetime_localized.strftime('%H-%M'),
                '_',
                instance.event.slug,
            )
        ),
        ''.join(
            (instance.event_container.mode, dot, extension,)
        )
    )
    # Абсолютный путь до файла
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    # Создание дерева папок до файла со стандартными правами 755
    if not os.path.exists(full_file_path):
        os.makedirs(os.path.dirname(full_file_path), mode=0o755, exist_ok=True)
    # Если файл уже был загружен ранее,
    # удаляем его и сохраняем новый файл с таким же именем
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)
    # Удаление старых пустых папок без изображений
    domain_subfolders = os.path.join(settings.MEDIA_ROOT, domain, instance._meta.app_label)
    for path, dirs, files in os.walk(domain_subfolders, topdown=False):
        if not dirs and not files:
            os.rmdir(path)

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
        verbose_name=_('eventcontainerbinder_event'),
    )
    event_container = models.ForeignKey(
        'event.EventContainer',
        on_delete=models.CASCADE,
        db_column='event_container_id',
        verbose_name=_('eventcontainerbinder_event_container'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('eventcontainerbinder_order'),
    )
    img = models.ImageField(
        upload_to=img_path,
        blank=True,
        null=True,
        verbose_name=_('eventcontainerbinder_img'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_container_binder'
        verbose_name = _('eventcontainerbinder')
        verbose_name_plural = _('eventcontainerbinders')
        ordering = ('order', 'event', 'event_container',)
        unique_together = (
            ('event', 'event_container', 'order',),
        )

    def __str__(self):
        return '{container} <-> {event}'.format(container=self.event_container, event=self.event)

    def delete(self, *args, **kwargs):
        full_file_path = os.path.join(settings.MEDIA_ROOT, str(self.img))
        if os.path.isfile(full_file_path):
            os.remove(full_file_path)

        super().delete(*args, **kwargs)

    def img_preview(self):
        return mark_safe(
            '<img class="img_preview_eventcontainerbinder" src="{url}">'.format(url=self.img.url)
        )
    img_preview.short_description = _('eventcontainerbinder_img_preview')

    def event_datetime_localized(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        # Дата и время события в часовом поясе его города
        current_timezone = self.event.domain.city.timezone
        event_datetime_localized = self.event.datetime.astimezone(current_timezone)
        return mark_safe(
            '{date} {time}'.format(
                date=naturalday(event_datetime_localized),
                time=event_datetime_localized.strftime('%H:%M'),
            )
        )
    event_datetime_localized.short_description = _('eventcontainerbinder_event_datetime')
