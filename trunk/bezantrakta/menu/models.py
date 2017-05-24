import uuid

from django.db import models

from bezantrakta.domain.models import Domain


class Menu(models.Model):
    """
    Меню для добавления пунктов меню с произвольными ссылками.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        verbose_name='Название меню',
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Псевдоним меню'
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Порядок в меню',
    )

    class Meta:
        app_label = 'menu'
        db_table = 'bezantrakta_menu'
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
        ordering = ('title', 'order',)

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    """
    Пункты меню с произвольными ссылками.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        verbose_name='Название пункта меню',
    )
    slug = models.SlugField(
        max_length=64,
        blank=True,
        help_text="""Псевдоним пункта меню должен совпадать
        с псевдонимом страницы, которую требуется в нём отобразить.""",
        verbose_name='Псевдоним пункта меню'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок в меню',
    )
    update_datetime = models.DateTimeField(
        auto_now=True,
        verbose_name='Сохранено',
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        db_column='menu_id',
        verbose_name='Меню',
    )
    domain = models.ForeignKey(
        Domain,
        # blank=True,
        # null=True,
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name='Домен',
    )

    class Meta:
        app_label = 'menu'
        db_table = 'bezantrakta_menu_item'
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Пункты меню'
        ordering = ('order', 'menu', 'domain', 'title',)
        unique_together = (
            ('domain', 'menu', 'slug',),
        )

    def __str__(self):
        return self.title
