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
