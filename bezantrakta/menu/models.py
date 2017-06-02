import uuid

from django.db import models


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

    class Meta:
        app_label = 'menu'
        db_table = 'bezantrakta_menu'
        verbose_name = 'меню'
        verbose_name_plural = 'меню'
        ordering = ('order', 'title',)

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
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=64,
        blank=True,
        help_text="""Псевдоним пункта меню должен совпадать
        с псевдонимом страницы, которую требуется в нём отобразить.""",
        verbose_name='Псевдоним'
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name='Публикация',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок в меню',
    )
    menu = models.ForeignKey(
        'menu.Menu',
        on_delete=models.CASCADE,
        db_column='menu_id',
        verbose_name='Меню',
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name='Домен',
    )

    class Meta:
        app_label = 'menu'
        db_table = 'bezantrakta_menu_item'
        verbose_name = 'пункт меню'
        verbose_name_plural = 'пункты меню'
        ordering = ('order', 'domain', 'menu', 'title',)
        unique_together = (
            ('domain', 'menu', 'slug',),
        )

    def __str__(self):
        return self.title
