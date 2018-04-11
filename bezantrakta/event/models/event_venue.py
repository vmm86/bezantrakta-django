import uuid

from django.db import models
from django.utils.translation import ugettext as _


class EventVenueManager(models.Manager):
    def get_queryset(self):
        return super(EventVenueManager, self).get_queryset().select_related(
            'city'
        ).prefetch_related(
            'ticketserviceschemevenuebinder_set'
        )


class EventVenue(models.Model):
    """Залы (места проведения событий).

    Attributes:
        objects (EventVenueManager): Менеджер модели.
        id (UUIDField): Уникальный идентификатор.
        slug (CharField): Псевдоним.
        title (SlugField): Название.
        city (ForeignKey): Привязка к городу, в котором находится зал.
    """
    objects = EventVenueManager()

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
    city = models.ForeignKey(
        'location.City',
        on_delete=models.CASCADE,
        db_column='city_id',
        verbose_name=_('eventvenue_city'),
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_venue'
        verbose_name = _('eventvenue')
        verbose_name_plural = _('eventvenues')
        ordering = ('city', 'title',)
        unique_together = (
            ('city', 'slug',),
        )

    def __str__(self):
        return '{title} ({city})'.format(title=self.title, city=self.city.title)
