from django.db import models


class City(models.Model):
    """
    Города России, в которых могут работать сайты Безантракта.
    """
    city_id = models.IntegerField(
        primary_key=True,
        unique=True,
    )
    city_title = models.CharField(
        max_length=64,
        verbose_name='Название города',
    )
    city_slug = models.SlugField(
        max_length=64,
        verbose_name='Псевдоним города',
    )
    city_status = models.BooleanField(
        default=False,
        help_text='True - готов к работе, False - скоро открытие',
        verbose_name='Готов ли город к работе',
    )

    class Meta:
        app_label = 'city'
        db_table = 'bezantrakta_city'
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ('city_title',)
        indexes = [
            models.Index(fields=['city_id']),
        ]

    def __str__(self):
        return self.city_title
