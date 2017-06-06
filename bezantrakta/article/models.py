import uuid

from ckeditor.fields import RichTextField

from django.db import models


class Article(models.Model):
    """
    Простые HTML-страницы.
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
        verbose_name='Псевдоним',
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
        verbose_name='Содержимое страницы',
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Публикация',
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name='Домен',
    )

    class Meta:
        app_label = 'article'
        db_table = 'bezantrakta_article'
        verbose_name = 'HTML-страница'
        verbose_name_plural = 'HTML-страницы'
        ordering = ('domain', 'title', 'is_published',)
        unique_together = (
            ('domain', 'slug',),
        )

    def __str__(self):
        return self.title