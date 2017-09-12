import uuid

from django.db import models
from django.urls.base import reverse
from django.utils.translation import ugettext as _

from ckeditor.fields import RichTextField


class ArticleManager(models.Manager):
    """Менеджер модели Article."""
    def get_queryset(self):
        return super(ArticleManager, self).get_queryset().select_related('domain')


class Article(models.Model):
    """Статические HTML-страницы.

    Attributes:
        objects (ArticleManager): Менеджер модели Article.
        id (UUIDField): Уникальный идентификатор.
        title (CharField): Название (всего не более 60-65 символов).
        slug (SlugField): Псевдоним.
        description (TextField): Метатег `description` (краткое описание страницы, не более 150-200 символов).
        keywords (TextField): Метатег `keywords` (ключевые слова/фразы, разделённые запятыми, описывающие содержимое страницы, всего не более 100-150 символов).
        text (RichTextField): Содержимое страницы.
        is_published (BooleanField): Опубликована ли страница на сайте или нет.
        domain (ForeignKey): Сайт.
    """
    objects = ArticleManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        help_text=_('article_title_help_text'),
        verbose_name=_('article_title'),
    )
    slug = models.SlugField(
        max_length=64,
        verbose_name=_('article_slug'),
    )
    description = models.TextField(
        max_length=200,
        help_text=_('article_description_help_text'),
        verbose_name=_('article_description'),
    )
    keywords = models.TextField(
        max_length=150,
        help_text=_('article_keywords_help_text'),
        verbose_name=_('article_keywords'),
    )
    text = RichTextField(
        verbose_name=_('article_text'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('article_is_published'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('article_domain'),
    )

    class Meta:
        app_label = 'article'
        db_table = 'bezantrakta_article'
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ('domain', 'title', 'is_published',)
        unique_together = (
            ('domain', 'slug',),
        )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article', args=[self.slug])
