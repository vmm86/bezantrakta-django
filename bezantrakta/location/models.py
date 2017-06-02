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
        verbose_name='Название города',
    )
    slug = models.SlugField(
        max_length=8,
        verbose_name='Псевдоним города',
    )
    timezone = TimeZoneField(
        default='Europe/Moscow',
        verbose_name='Часовой пояс',
    )
    is_published = models.BooleanField(
        default=False,
        help_text="""
        True - включен и работает,
        False - отключен (скоро открытие).""",
        verbose_name='Публикация',
    )

    class Meta:
        app_label = 'location'
        db_table = 'bezantrakta_location_city'
        verbose_name = 'город'
        verbose_name_plural = 'города'
        ordering = ('title',)

    def __str__(self):
        return self.title


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
