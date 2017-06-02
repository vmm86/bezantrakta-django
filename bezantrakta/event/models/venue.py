import uuid

from django.db import models


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
        help_text='Всего не более 60-65 символов',
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name='Псевдоним'
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name='Домен',
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_venue'
        verbose_name = 'зал'
        verbose_name_plural = 'залы'
        ordering = ('domain', 'title',)
        unique_together = (
            ('domain', 'slug',),
        )

    def __str__(self):
        return self.title
