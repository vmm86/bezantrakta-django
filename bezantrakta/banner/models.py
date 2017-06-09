import os
import uuid

from django.conf import settings
from django.db import models


class BannerGroup(models.Model):
    """
    Группы баннеров для показа в разных блоках в шаблоне сайта.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=32,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Псевдоним',
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        null=False,
        verbose_name='Порядок',
    )

    class Meta(object):
        app_label = 'banner'
        db_table = 'bezantrakta_banner_group'
        verbose_name = 'группа баннеров'
        verbose_name_plural = 'группы баннеров'
        ordering = ('order', 'title',)

    def __str__(self):
        return self.title


def img_path(instance, filename):
    if instance.domain is None:
        domain = 'global'
    else:
        domain = instance.domain.slug

    name, dot, extension = filename.rpartition('.')
    # Относительный путь до файла
    file_path = os.path.join(
        domain,
        instance._meta.app_label,
        instance.banner_group.slug,
        ''.join(
            (instance.slug, dot, extension,)
        )
    )
    # Абсолютный путь до файла
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    # Если файл уже был загружен ранее,
    # удаляем его и сохраняем новый файл с таким же именем
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)

    return file_path


class BannerGroupItem(models.Model):
    """
    Баннеры, входящие в какую-то группу баннеров.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=32,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Псевдоним',
    )
    img = models.ImageField(
        upload_to=img_path,
        verbose_name='Изображение'
    )
    href = models.URLField(
        blank=True,
        verbose_name='Внешняя ссылка',
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Публикация',
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        null=False,
        verbose_name='Порядок',
    )
    banner_group = models.ForeignKey(
        'banner.BannerGroup',
        on_delete=models.CASCADE,
        db_column='banner_group_id',
        verbose_name='Группа баннеров',
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name='Домен',
    )

    class Meta(object):
        app_label = 'banner'
        db_table = 'bezantrakta_banner_group_item'
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'
        ordering = ('order', 'banner_group', 'domain', 'title',)
        unique_together = (
            ('domain', 'banner_group', 'slug',),
        )

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        full_file_path = os.path.join(settings.MEDIA_ROOT, str(self.img))
        if os.path.isfile(full_file_path):
            os.remove(full_file_path)

        super().delete(*args, **kwargs)
