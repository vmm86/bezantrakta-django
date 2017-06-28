import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


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
        verbose_name=_('bannergroup_title'),
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('bannergroup_slug'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        null=False,
        verbose_name=_('bannergroup_order'),
    )

    class Meta(object):
        app_label = 'banner'
        db_table = 'bezantrakta_banner_group'
        verbose_name = _('bannergroup')
        verbose_name_plural = _('bannergroups')
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
    # Создание дерева папок до файла со стандартными правами 755
    if not os.path.exists(full_file_path):
        os.makedirs(os.path.dirname(full_file_path), mode=0o755, exist_ok=True)
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
        verbose_name=_('bannergroupitem_title'),
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('bannergroupitem_slug'),
    )
    img = models.ImageField(
        upload_to=img_path,
        verbose_name=_('bannergroupitem_img')
    )
    href = models.URLField(
        blank=True,
        verbose_name=_('bannergroupitem_href'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('bannergroupitem_is_published'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        blank=False,
        null=False,
        verbose_name=_('bannergroupitem_order'),
    )
    banner_group = models.ForeignKey(
        'banner.BannerGroup',
        on_delete=models.CASCADE,
        db_column='banner_group_id',
        verbose_name=_('bannergroupitem_banner_group'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('bannergroupitem_domain'),
    )

    class Meta(object):
        app_label = 'banner'
        db_table = 'bezantrakta_banner_group_item'
        verbose_name = _('bannergroupitem')
        verbose_name_plural = _('bannergroupitems')
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
