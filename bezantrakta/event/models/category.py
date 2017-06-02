import uuid

from django.db import models


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
        help_text='Всего не более 60-65 символов',
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=64,
        unique=True,
        verbose_name='Псевдоним'
    )
    description = models.CharField(
        max_length=200,
        help_text="""Должно сдержать ключевые слова или фразы,
        описывающие событие, но не более 3-5 раз.\n
        Всего не более 150-200 символов""",
        verbose_name='Метатег `description`',
    )
    keywords = models.CharField(
        max_length=150,
        help_text="""Несколько ключевых слов или фраз,
        разделённых запятыми, которые описывают содержимое текста.\n
        Всего не более 100-150 символов""",
        verbose_name='Метатег `keywords`',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Публикация',
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event_category'
        verbose_name = 'Категория событий'
        verbose_name_plural = 'Категории событий'
        ordering = ('title',)

    def __str__(self):
        return self.title
