import datetime

from django.db import models
from django.utils.translation import ugettext as _

from timezone_field import TimeZoneField


def timezone_offset_humanized(timezone):
    """Вывод человекопонятной разницы часовых поясов с UTC.

    Args:
        timezone (timezone): Часовой пояс.

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
        id (IntegerField): Идентификатор (телефонный код города).
        title (CharField): Название.
        slug (SlugField): Псевдоним (не более 5-7 знаков, наиболее употребимое сокращение название города в Интернете).
        timezone (TimeZoneField): Часовой пояс города.
        state (NullBooleanField): Состояние города, берущееся из ``STATE_CHOICES``.

            Содержимое ``STATE_CHOICES`` (кортеж из кортежей "значение" / "подпись").
                    * **STATE_DISABLED** (bool): Выключен (``False``).
                    * **STATE_PROGRESS** (None): В процессе подготовки ("скоро открытие") (``None``).
                    * **STATE_ENABLED** (bool):  Включен (``True``).
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

    def state_icons(self):
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        if self.state is False:
            return _boolean_icon(False)
        elif self.state is None:
            return _boolean_icon(None)
        elif self.state is True:
            return _boolean_icon(True)
    state_icons.short_description = _('city_state_icons')

    def timezone_offset(self):
        return '{offset} {timezone}'.format(
            offset=timezone_offset_humanized(self.timezone),
            timezone=self.timezone,
        )
    timezone_offset.short_description = _('city_timezone')
