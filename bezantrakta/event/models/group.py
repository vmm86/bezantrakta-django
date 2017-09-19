import uuid

from django.db import models
from django.utils.translation import ugettext as _


class EventGroup(models.Model):
    """
    Группы событий.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        help_text=_('eventgroup_title_help_text'),
        verbose_name=_('eventgroup_title'),
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name=_('eventgroup_slug'),
    )
    description = models.TextField(
        max_length=200,
        help_text=_('eventgroup_description_help_text'),
        verbose_name=_('eventgroup_description'),
    )
    keywords = models.TextField(
        max_length=150,
        help_text=_('eventgroup_keywords_help_text'),
        verbose_name=_('eventgroup_keywords'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('eventgroup_is_published'),
    )
    is_on_index = models.BooleanField(
        default=False,
        verbose_name=_('eventgroup_is_on_index'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('eventgroup_domain'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_group'
        verbose_name = _('eventgroup')
        verbose_name_plural = _('eventgroups')
        ordering = ('id', 'title',)
        unique_together = (
            ('domain', 'slug',),
        )

    def __str__(self):
        return self.title
