import datetime
import json
import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from timezone_field import TimeZoneField


def timezone_offset_humanized(timezone):
    offset = datetime.datetime.now(timezone).utcoffset()
    seconds = offset.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    sign = '+' if offset >= datetime.timedelta(0) else '-'

    return '{sign}{hours}:{minutes}'.format(
        sign=sign,
        hours=str(hours).zfill(2),
        minutes=str(minutes).zfill(2)
    )


class City(models.Model):
    """
    Города России, в которых могут работать сайты Безантракта.
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


def get_default_domain_settings():
    domain_settings_file = os.path.join(
        settings.BASE_DIR,
        'bezantrakta',
        'location',
        'domain_settings.json',
    )
    with open(domain_settings_file, 'r') as dsf:
        return json.dumps(json.load(dsf), ensure_ascii=False)


class Domain(models.Model):
    """
    Сайты Безантракта, работающие в разных городах России.
    """
    id = models.IntegerField(
        primary_key=True,
        help_text=_('domain_id_help_text'),
        verbose_name=_('domain_id'),
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('domain_title'),
    )
    slug = models.CharField(
        max_length=32,
        unique=True,
        help_text=_('domain_slug_help_text'),
        verbose_name=_('domain_slug'),
    )
    is_published = models.BooleanField(
        default=False,
        help_text=_('domain_is_published_help_text'),
        verbose_name=_('domain_is_published'),
    )
    city = models.ForeignKey(
        'location.City',
        on_delete=models.CASCADE,
        db_column='city_id',
        verbose_name=_('domain_city'),
    )
    settings = models.TextField(
        default=get_default_domain_settings,
        verbose_name=_('domain_settings'),
    )

    class Meta:
        app_label = 'location'
        db_table = 'bezantrakta_location_domain'
        verbose_name = _('domain')
        verbose_name_plural = _('domains')
        ordering = ('city', 'title',)

    def __str__(self):
        return '{title} - {slug}'.format(title=self.title, slug=self.slug)