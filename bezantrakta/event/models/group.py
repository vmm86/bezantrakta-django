import uuid

from django.db import models


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
        help_text='Всего не более 60-65 символов',
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name='Псевдоним'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Публикация',
    )
    is_on_index = models.BooleanField(
        default=False,
        verbose_name='На главной',
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name='Домен',
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_group'
        verbose_name = 'группа событий'
        verbose_name_plural = 'группы событий'
        ordering = ('id', 'title',)
        unique_together = (
            ('domain', 'slug',),
        )

    def __str__(self):
        return self.title
