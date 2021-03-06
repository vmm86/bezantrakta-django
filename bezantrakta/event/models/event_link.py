import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


def img_path(instance, filename):
    """Обработка загрузки изображения на сайт."""
    name, dot, extension = filename.rpartition('.')
    # Относительный путь до файла
    file_path = os.path.join(
        'global',
        'link',
        '{slug}.{ext}'.format(slug=instance.slug, ext=extension)
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

    return file_path


class EventLink(models.Model):
    """Внешние ссылки на сторонних продавцов билетов на события.

    Перечень сайтов (с логотипами или без), на которые могут вести опциональные внешние ссылки.
    Эти ссылки можно добавлять к событиям (независимо от того, привязано событие к билетному сервису или нет).

    Attributes:
        id (UUIDField): Уникальный идентификатор.
        title (CharField): Название.
        slug (SlugField): Псевдоним.
        img (ImageField): Путь к файлу с иконкой стороннего продавца билетов внутри ``settings.MEDIA_ROOT``.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=32,
        verbose_name=_('eventlink_title'),
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('eventlink_slug'),
    )
    img = models.ImageField(
        upload_to=img_path,
        blank=True,
        null=True,
        help_text=_('eventlink_img_help_text'),
        verbose_name=_('eventlink_img'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_link'
        verbose_name = _('eventlink')
        verbose_name_plural = _('eventlinks')
        ordering = ('title',)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """Удаление файла изображения перед удалением записи в БД."""
        full_file_path = os.path.join(settings.MEDIA_ROOT, str(self.img))
        if os.path.isfile(full_file_path):
            os.remove(full_file_path)

        super().delete(*args, **kwargs)

    def img_preview(self):
        """Вывод иконки с изображением внешней ссылки."""
        return mark_safe('<img class="img_preview_link" src="{url}">'.format(url=self.img.url))
    img_preview.short_description = _('eventlinks_img_preview')
