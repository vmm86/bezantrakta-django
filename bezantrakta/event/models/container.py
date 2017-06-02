import uuid

from django.db import models


class EventContainer(models.Model):
    """
    Контейнеры для отображения событий на сайте.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=32,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Псевдоним'
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Порядок',
    )
    img_width = models.PositiveSmallIntegerField(
        verbose_name='Ширина афиши',
    )
    img_height = models.PositiveSmallIntegerField(
        verbose_name='Высота афиши',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Публикация',
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_container'
        verbose_name = 'Контейнер'
        verbose_name_plural = 'Контейнеры'
        ordering = ('order', 'is_published', 'title',)

    def __str__(self):
        return self.title
