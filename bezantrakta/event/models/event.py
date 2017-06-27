import uuid

from ckeditor.fields import RichTextField

from django.db import models
from django.urls.base import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


class Event(models.Model):
    """
    События, привязанные к какому-то билетному сервису или независимые.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        help_text=_('event_title_help_text'),
        verbose_name=_('event_title'),
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name=_('event_slug'),
    )
    description = models.TextField(
        max_length=200,
        help_text=_('event_description_help_text'),
        verbose_name=_('event_description'),
    )
    keywords = models.TextField(
        max_length=150,
        help_text=_('event_keywords_help_text'),
        verbose_name=_('event_keywords'),
    )
    text = RichTextField(
        verbose_name=_('event_text'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('event_is_published'),
    )
    is_on_index = models.BooleanField(
        default=False,
        verbose_name=_('event_is_on_index'),
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('event_min_price'),
    )
    AGE_00 = 0
    AGE_06 = 6
    AGE_12 = 12
    AGE_16 = 16
    AGE_18 = 18
    MIN_AGE_CHOICES = (
        (AGE_00, '0+'),
        (AGE_06, '6+'),
        (AGE_12, '12+'),
        (AGE_16, '16+'),
        (AGE_18, '18+'),
    )
    min_age = models.PositiveSmallIntegerField(
        choices=MIN_AGE_CHOICES,
        default=AGE_00,
        blank=False,
        verbose_name=_('event_min_age'),
    )
    datetime = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('event_datetime'),
    )
    event_group = models.ManyToManyField(
        'event.EventGroup',
        through='event.EventGroupBinder',
        blank=True,
        verbose_name=_('event_event_group'),
    )
    event_container = models.ManyToManyField(
        'event.EventContainer',
        through='event.EventContainerBinder',
        blank=True,
        verbose_name=_('event_event_container'),
    )
    event_link = models.ManyToManyField(
        'event.EventLink',
        through='event.EventLinkBinder',
        blank=True,
        verbose_name=_('event_event_link'),
    )
    event_category = models.ForeignKey(
        'event.EventCategory',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_column='event_category_id',
        verbose_name=_('event_event_category'),
    )
    event_venue = models.ForeignKey(
        'event.EventVenue',
        on_delete=models.CASCADE,
        db_column='event_venue_id',
        verbose_name=_('event_event_venue'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('event_domain'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event'
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('domain', 'datetime', 'title',)
        unique_together = (
            ('domain', 'datetime', 'slug',),
        )

    def __str__(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        # Дата и время события в часовом поясе его города
        current_timezone = self.domain.city.timezone
        event_datetime_localized = self.datetime.astimezone(current_timezone)
        return '{title} ({date} {time})'.format(
            title=self.title,
            date=naturalday(event_datetime_localized),
            time=event_datetime_localized.strftime('%H:%M')
        )

    def get_absolute_url(self):
        return reverse(
            'event',
            args=[
                str(self.datetime.year),
                str(self.datetime.month),
                str(self.datetime.day),
                str(self.datetime.hour),
                str(self.datetime.minute),
                self.slug
            ]
        )

    def datetime_localized(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        # Дата и время события в часовом поясе его города
        current_timezone = self.domain.city.timezone
        event_datetime_localized = self.datetime.astimezone(current_timezone)
        return mark_safe(
            '{date} {time}'.format(
                date=naturalday(event_datetime_localized),
                time=event_datetime_localized.strftime('%H:%M'),
            )
        )
    datetime_localized.short_description = _('event_datetime')

    def container_count(self):
        return self.event_container.count()
    container_count.short_description = _('event_container_count')

    def link_count(self):
        return self.event_link.count()
    link_count.short_description = _('event_link_count')
