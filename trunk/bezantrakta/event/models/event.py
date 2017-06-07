import uuid

from ckeditor.fields import RichTextField

from django.db import models


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
        help_text='Всего не более 60-65 символов',
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=64,
        unique_for_date='date',
        verbose_name='Псевдоним'
    )
    description = models.TextField(
        max_length=200,
        help_text="""Должно сдержать ключевые слова или фразы,
        описывающие событие, но не более 3-5 раз.\n
        Всего не более 150-200 символов""",
        verbose_name='Метатег `description`',
    )
    keywords = models.TextField(
        max_length=150,
        help_text="""Несколько ключевых слов или фраз,
        разделённых запятыми, которые описывают содержимое текста.\n
        Всего не более 100-150 символов""",
        verbose_name='Метатег `keywords`',
    )
    text = RichTextField(
        verbose_name='Описание события',
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Публикация',
    )
    is_on_index = models.BooleanField(
        default=False,
        verbose_name='На главной',
    )
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Минимальная цена билета',
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
        verbose_name='Возрастное ограничение',
    )
    date = models.DateField(
        verbose_name='Дата события',
    )
    time = models.TimeField(
        verbose_name='Время начала события',
    )
    event_group = models.ManyToManyField(
        'event.EventGroup',
        through='event.EventGroupBinder',
        blank=True,
        verbose_name='Группа, в которую входит событие',
    )
    event_container = models.ManyToManyField(
        'event.EventContainer',
        through='event.EventContainerBinder',
        blank=True,
        verbose_name='Контейнеры, в которых отображается событие',
    )
    event_link = models.ManyToManyField(
        'event.EventLink',
        through='event.EventLinkBinder',
        blank=True,
        verbose_name='Ссылки, добавленные к событию',
    )
    event_category = models.ForeignKey(
        'event.EventCategory',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        db_column='event_category_id',
        verbose_name='Категория',
    )
    event_venue = models.ForeignKey(
        'event.EventVenue',
        on_delete=models.CASCADE,
        db_column='event_venue_id',
        verbose_name='Зал',
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name='Домен',
    )

    class Meta:
        app_label = 'event'
        db_table = 'bezantrakta_event'
        verbose_name = 'событие'
        verbose_name_plural = 'события'
        ordering = ('domain', 'date', 'time', 'title',)
        unique_together = (
            ('domain', 'date', 'slug',),
        )

    def __str__(self):
        return self.title

    def container_count(self):
        return self.event_container.count()
    container_count.short_description = 'Контейнеров'

    def link_count(self):
        return self.event_link.count()
    link_count.short_description = 'Ссылок'
