import uuid

from django.db import models
from django.utils.translation import ugettext as _


class EventContainer(models.Model):
    """Контейнеры для отображения событий на сайте в разных позициях в базовом шаблоне.

    Attributes:
        id (UUIDField): Уникальный идентификатор.
        title (CharField): Название.
        slug (SlugField): Псевдоним.
        mode (CharField): Тип контейнера, берущийся из ``MODE_CHOICES`` (по умолчанию - ``small_vertical``).

            Содержимое ``MODE_CHOICES`` (кортеж из кортежей "значение" / "подпись").
                * **MODE_BV** (str): Большие вертикальные афиши (``big_vertical``).
                * **MODE_BH** (str): Большие горизонтальные афиши (``big_vertical``).
                * **MODE_SV** (str): Маленькие вертикальные афиши (``small_vertical``).
                * **MODE_SH** (str): Маленькие горизонтальные афиши (``small_horizontal``).

        order (PositiveSmallIntegerField): Порядок контейнеров в админ-панели.
        img_width (PositiveSmallIntegerField): Ширина афиши в контейнере (для справки, функционально не используется).
        img_height (PositiveSmallIntegerField): Высота афиши в контейнере (для справки, функционально не используется).
        is_published (BooleanField): Опубликовано (``True``) или НЕ опубликовано (``False``).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('eventcontainer_title'),
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name=_('eventcontainer_slug'),
    )
    MODE_BV = 'big_vertical'
    MODE_BH = 'big_horizontal'
    MODE_SV = 'small_vertical'
    MODE_SH = 'small_horizontal'
    MODE_CHOICES = (
        (MODE_BV, _('eventcontainer_mode_big_vertical')),
        (MODE_BH, _('eventcontainer_mode_big_horizontal')),
        (MODE_SV, _('eventcontainer_mode_small_vertical')),
        (MODE_SH, _('eventcontainer_mode_small_horizontal')),
    )
    mode = models.CharField(
        choices=MODE_CHOICES,
        default=MODE_SV,
        blank=False,
        max_length=16,
        db_index=True,
        verbose_name=_('eventcontainer_mode'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('eventcontainer_order'),
    )
    img_width = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_('eventcontainer_img_width'),
    )
    img_height = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_('eventcontainer_img_height'),
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_('eventcontainer_is_published'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_container'
        verbose_name = _('eventcontainer')
        verbose_name_plural = _('eventcontainers')
        ordering = ('order', 'is_published', 'title',)

    def __str__(self):
        return '{width}x{height} px - {title}'.format(width=self.img_width, height=self.img_height, title=self.title)
