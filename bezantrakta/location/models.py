from django.db import models

from timezone_field import TimeZoneField


class City(models.Model):
    """
    Города России, в которых могут работать сайты Безантракта.
    """
    id = models.IntegerField(
        primary_key=True,
    )
    title = models.CharField(
        max_length=64,
        verbose_name='Название',
    )
    slug = models.SlugField(
        max_length=8,
        verbose_name='Псевдоним',
    )
    timezone = TimeZoneField(
        default='Europe/Moscow',
        verbose_name='Часовой пояс',
    )
    STATE_DISABLED = False
    STATE_PROGRESS = None
    STATE_ENABLED = True
    STATE_CHOICES = (
        (STATE_DISABLED, 'отключен'),
        (STATE_PROGRESS, 'подготовка'),
        (STATE_ENABLED, 'включен'),
    )
    state = models.NullBooleanField(
        choices=STATE_CHOICES,
        default=STATE_DISABLED,
        blank=False,
        help_text="""
        <ul>
        <li>отключен - НЕ виден в списке городов и НЕ работает;</li>
        <li>подготовка - виден в списке городов, но НЕ доступен для выбора ("скоро открытие");</li>
        <li>включен - виден в списке городов и работает.</li>
        </ul>
        """,
        verbose_name='Состояние',
    )

    class Meta:
        app_label = 'location'
        db_table = 'bezantrakta_location_city'
        verbose_name = 'город'
        verbose_name_plural = 'города'
        ordering = ('title',)

    def __str__(self):
        return self.title

    def state_icons(self):
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        if self.state is False:
            return _boolean_icon(False)
        elif self.state is None:
            return _boolean_icon(None)
        elif self.state is True:
            return _boolean_icon(True)
    state_icons.short_description = 'Состояние'


class Domain(models.Model):
    """
    Сайты Безантракта, работающие в разных городах России.
    """
    id = models.IntegerField(
        primary_key=True
    )
    title = models.CharField(
        max_length=64,
        verbose_name='Название',
    )
    slug = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Псевдоним',
    )
    is_published = models.BooleanField(
        default=False,
        help_text="""
        True - включен и работает,
        False - отключен (сайт недоступен, проводятся технические работы).""",
        verbose_name='Публикация',
    )
    city = models.ForeignKey(
        'location.City',
        on_delete=models.CASCADE,
        db_column='city_id',
        verbose_name='Город',
    )

    class Meta:
        app_label = 'location'
        db_table = 'bezantrakta_location_domain'
        verbose_name = 'домен'
        verbose_name_plural = 'домены'
        ordering = ('city', 'title',)

    def __str__(self):
        return self.title
