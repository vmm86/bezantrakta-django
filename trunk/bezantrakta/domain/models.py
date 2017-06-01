import string

from django.core.exceptions import ValidationError
from django.db import models


def _domain_name_validator(value):
    """
    Простая валидация на отсутствие пробелов.
    """
    if not value:
        return
    checks = ((s in value) for s in string.whitespace)
    if any(checks):
        raise ValidationError(
            'Имя домена не может содержать пробелы или символы табуляции!',
            code='invalid',
        )


class Domain(models.Model):
    """
    Сайты Безантракта, работающие в разных городах России.
    """
    id = models.IntegerField(
        primary_key=True
    )
    title = models.CharField(
        max_length=64,
        verbose_name='Название домена',
    )
    slug = models.CharField(
        max_length=32,
        validators=[_domain_name_validator],
        unique=True,
        verbose_name='Псевдоним домена',
    )
    is_published = models.BooleanField(
        default=False,
        help_text="""
        True - включен и работает,
        False - отключен (сайт недоступен, проводятся технические работы).""",
        verbose_name='Включен/отключен',
    )
    city = models.ForeignKey(
        'city.City',
        on_delete=models.CASCADE,
        db_column='city_id',
        verbose_name='Город',
    )

    class Meta:
        app_label = 'domain'
        db_table = 'bezantrakta_domain'
        verbose_name = 'Домен'
        verbose_name_plural = 'Домены'
        ordering = ('city', 'title',)

    def __str__(self):
        return self.title

    def get_domains(self):
        return self.objects.all().values_list('slug')
