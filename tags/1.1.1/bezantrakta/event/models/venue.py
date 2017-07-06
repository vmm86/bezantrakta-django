import uuid

from django.db import models
from django.utils.translation import ugettext as _


class EventVenue(models.Model):
    """
    Залы, в которых проходят события.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('eventvenue_title'),
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name=_('eventvenue_slug'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('eventvenue_domain'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_venue'
        verbose_name = _('eventvenue')
        verbose_name_plural = _('eventvenues')
        ordering = ('domain', 'title',)
        unique_together = (
            ('domain', 'slug',),
        )

    def __str__(self):
        return '{venue} - {city}'.format(venue=self.title, city=self.domain.city.title)
