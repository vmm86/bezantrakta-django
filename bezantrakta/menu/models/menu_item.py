import uuid

from django.db import models
from django.utils.translation import ugettext as _


class MenuItemManager(models.Manager):
    def get_queryset(self):
        return super(MenuItemManager, self).get_queryset().select_related('menu', 'domain')


class MenuItem(models.Model):
    """Пункты меню с произвольными ссылками (абсолютными внешними или относительными локальными).

    Attributes:
        objects (MenuItemManager): Description
        id (UUIDField): Уникальный идентификатор.
        title (CharField): Название.
        slug (SlugField): Псевдоним.
        is_published (BooleanField): Опубликовано (``True``) или НЕ опубликовано (``False``).
        order (PositiveSmallIntegerField): Порядок пунктов меню в меню.
        menu (ForeignKey): Привязка с меню.
        domain (ForeignKey): Привязка с сайту.
    """
    objects = MenuItemManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(
        max_length=64,
        verbose_name=_('menuitem_title'),
    )
    slug = models.CharField(
        max_length=128,
        blank=True,
        help_text=_('menuitem_slug_help_text'),
        verbose_name=_('menuitem_slug'),
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('menuitem_is_published'),
    )
    order = models.PositiveSmallIntegerField(
        default=1,
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
