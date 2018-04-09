import datetime
import os
from random import randint

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from timezone_field import TimeZoneField


def img_path(instance, filename):
    name, dot, extension = filename.rpartition('.')
    # Относительный путь до файла
    file_path = os.path.join(
        'global',
        'city',
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


def timezone_offset_humanized(timezone):
    """Вывод человекопонятной разницы часовых поясов с ``UTC``.

    Args:
        timezone (timezone): Часовой пояс из ``pytz``.

    Returns:
        str: Разница часового пояса с UTC в формате ``±ЧАСОВ:МИНУТ``.
    """
    offset = datetime.datetime.now(timezone).utcoffset()
    seconds = offset.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if offset > datetime.timedelta(0):
        sign = '+'
    elif offset == datetime.timedelta(0):
        sign = '±'
    elif offset < datetime.timedelta(0):
        sign = '−'

    return '{sign}{hours}:{minutes}'.format(
        sign=sign,
        hours=str(hours).zfill(2),
        minutes=str(minutes).zfill(2)
    )


class City(models.Model):
    """Города России, в которых могут работать сайты Безантракта.

    Attributes:
        id (django.db.models.IntegerField): Идентификатор (телефонный код города).
        title (django.db.models.CharField): Название.
        slug (django.db.models.SlugField): Псевдоним (не более 3-5 символов).
        timezone (django.db.models.TimeZoneField): Часовой пояс города.
        state (django.db.models.NullBooleanField): Состояние города, берущееся из ``STATE_CHOICES``.

            Содержимое ``STATE_CHOICES`` (кортеж из кортежей "значение" / "подпись").
                * **STATE_DISABLED** (bool): Выключен (``False``).
                * **STATE_PROGRESS** (None): В процессе подготовки ("скоро открытие") (``None``).
                * **STATE_ENABLED** (bool): Включен (``True``).
    """
    id = models.IntegerField(
        primary_key=True,
        help_text=_('city_id_help_text'),
        verbose_name=_('city_id'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('city_title'),
    )
    slug = models.SlugField(
        max_length=8,
        verbose_name=_('city_slug'),
    )
    timezone = TimeZoneField(
        default='Europe/Moscow',
        verbose_name=_('city_timezone'),
    )
    icon = models.ImageField(
        upload_to=img_path,
        verbose_name=_('city_icon')
    )
    STATE_DISABLED = False
    STATE_PROGRESS = None
    STATE_ENABLED = True
    STATE_CHOICES = (
        (STATE_DISABLED, _('city_state_disabled')),
        (STATE_PROGRESS, _('city_state_progress')),
        (STATE_ENABLED, _('city_state_enabled')),
    )
    state = models.NullBooleanField(
        choices=STATE_CHOICES,
        default=STATE_DISABLED,
        blank=False,
        help_text=_('city_state_help_text'),
        verbose_name=_('city_state'),
    )

    class Meta:
        app_label = 'location'
        db_table = 'bezantrakta_location_city'
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        ordering = ('title',)

    def __str__(self):
        return '{title} - {slug}'.format(title=self.title, slug=self.slug)

    def img_preview(self):
        if self.icon:
            return mark_safe('<img class="img_preview_city" src="{media}{url}?{reload}" width="100" height="100">'.format(
                media=settings.MEDIA_URL,
                url=self.icon,
                reload=randint(1, 100))
            )
        else:
            return ''
    img_preview.short_description = _('city_img_preview')

    def ico_preview(self):
        if self.icon:
            return mark_safe('<img class="img_preview_city" src="{media}{url}?{reload}" width="32" height="32">'.format(
                media=settings.MEDIA_URL,
                url=self.icon,
                reload=randint(1, 100))
            )
        else:
            return ''
    ico_preview.short_description = _('city_img_preview')

    def timezone_offset(self):
        """Вывод разницы во времени с ``UTC`` у часового пояса города.

        Returns:
            str: Строка с указанием разницы во времени.
        """
        return '{offset} {timezone}'.format(
            offset=timezone_offset_humanized(self.timezone),
            timezone=self.timezone,
        )
    timezone_offset.short_description = _('city_timezone')

    def state_icons(self):
        """Вывод иконок для обозначения статуса города в списке записей в админ-панели.

        Returns:
            str: HTML-разметка для вывода иконки статуса.
        """
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        if self.state is False:
            return _boolean_icon(False)
        elif self.state is None:
            return _boolean_icon(None)
        elif self.state is True:
            return _boolean_icon(True)
    state_icons.short_description = _('city_state_icons')
    state_icons.admin_order_field = 'state'
