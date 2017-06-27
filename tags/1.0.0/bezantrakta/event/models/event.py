import uuid

from ckeditor.fields import RichTextField

from django.db import models
from django.urls.base import reverse
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
    date = models.DateField(
        verbose_name=_('event_date'),
    )
    time = models.TimeField(
        verbose_name=_('event_time'),
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
        ordering = ('domain', 'date', 'time', 'title',)
        unique_together = (
            ('domain', 'date', 'slug',),
        )

    def __str__(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        return '{} ({})'.format(self.title, naturalday(self.date),)

    def get_absolute_url(self):
        return reverse(
            'event',
            args=[
                str(self.date.year),
                str(self.date.month),
                str(self.date.day),
                self.slug
            ]
        )

    def container_count(self):
        return self.event_container.count()
    container_count.short_description = _('event_container_count')

    def link_count(self):
        return self.event_link.count()
    link_count.short_description = _('event_link_count')
