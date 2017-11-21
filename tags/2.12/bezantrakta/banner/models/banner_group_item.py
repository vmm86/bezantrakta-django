import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _


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


class BannerGroupItemManager(models.Manager):
    def get_queryset(self):
        return super(BannerGroupItemManager, self).get_queryset().select_related('domain')


class BannerGroupItem(models.Model):
    """Баннеры, входящие в какую-то группу баннеров.

    Attributes:
        objects (BannerGroupItemManager): Менеджер модели.
        id (UUIDField): Уникальный идентификатор.
        title (CharField): Название.
        slug (SlugField): Псевдоним.
        img (ImageField): Путь к файлу с иконкой баннера внутри ``settings.MEDIA_ROOT``.
        href (URLField): Внешняя ссылка, на которую ведёт баннер.
        is_published (BooleanField): Включен (``True``) или отключен (``False``).
        order (PositiveSmallIntegerField): Порядок следования в группе баннеров.
        banner_group (ForeignKey): Принадлежность к группе баннеров.
        domain (ForeignKey): Принадлежность к сайту.
    """
    objects = BannerGroupItemManager()

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
    href = models.CharField(
        max_length=128,
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
