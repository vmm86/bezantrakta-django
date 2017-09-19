import uuid

from django.db import models
from django.urls.base import reverse
from django.utils.translation import ugettext as _


class EventCategory(models.Model):
    """
    Категории событий (концерты, спектакли и т.п.).
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        help_text=_('eventcategory_title_help_text'),
        verbose_name=_('eventcategory_title'),
    )
    slug = models.SlugField(
        max_length=64,
        unique=True,
        verbose_name=_('eventcategory_slug'),
    )
    description = models.CharField(
        max_length=200,
        help_text=_('eventcategory_description_help_text'),
        verbose_name=_('eventcategory_description'),
    )
    keywords = models.CharField(
        max_length=150,
        help_text=_('eventcategory_keywords_help_text'),
        verbose_name=_('eventcategory_keywords'),
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name=_('eventcategory_is_published'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_category'
        verbose_name = _('eventcategory')
        verbose_name_plural = _('eventcategories')
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category', args=[self.slug])
