import uuid

from django.db import models
from django.utils.translation import ugettext as _


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
        verbose_name=_('menu_title'),
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name=_('menu_slug'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('menu_order'),
    )

    class Meta:
        app_label = 'menu'
        db_table = 'bezantrakta_menu'
        verbose_name = _('menu')
        verbose_name_plural = _('menus')
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
        verbose_name=_('menuitem_title'),
    )
    slug = models.SlugField(
        max_length=64,
        blank=True,
        help_text=_('menuitem_slug_help_text'),
        verbose_name=_('menuitem_slug'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('menuitem_is_published'),
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('menuitem_order'),
    )
    menu = models.ForeignKey(
        'menu.Menu',
        on_delete=models.CASCADE,
        db_column='menu_id',
        verbose_name=_('menuitem_menu'),
    )
    domain = models.ForeignKey(
        'location.Domain',
        on_delete=models.CASCADE,
        db_column='domain_id',
        verbose_name=_('menuitem_domain'),
    )

    class Meta:
        app_label = 'menu'
        db_table = 'bezantrakta_menu_item'
        verbose_name = _('menuitem')
        verbose_name_plural = _('menuitems')
        ordering = ('order', 'domain', 'menu', 'title',)
        unique_together = (
            ('domain', 'menu', 'slug',),
        )

    def __str__(self):
        return self.title
