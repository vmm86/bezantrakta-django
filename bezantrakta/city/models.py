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
    status = models.BooleanField(
        default=False,
        help_text="""
        True - включен и работает,
        False - отключен (делает недоступными все сайты в этом городе).""",
        verbose_name='Включен/отключен',
    )
    timezone = TimeZoneField(
        default='Europe/Moscow',
        verbose_name='Часовой пояс',
    )

    class Meta:
        app_label = 'city'
        db_table = 'bezantrakta_city'
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ('title',)

    def __str__(self):
        return self.title
