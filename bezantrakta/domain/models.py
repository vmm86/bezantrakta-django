import string

from django.core.exceptions import ValidationError
from django.db import models

from city.models import City


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
    domain_id = models.IntegerField(
        primary_key=True
    )
    domain_title = models.CharField(
        max_length=50,
        verbose_name='Название домена',
    )
    domain_slug = models.SlugField(
        max_length=100,
        validators=[_domain_name_validator],
        unique=True,
        verbose_name='Псевдоним домена',
    )
    city_id = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        db_column='city_id'
    )

    class Meta:
        app_label = 'domain'
        db_table = 'bezantrakta_domain'
        verbose_name = 'Домен'
        verbose_name_plural = 'Домены'
        ordering = ('city_id', 'domain_title',)
        indexes = [
            models.Index(fields=['domain_id']),
        ]

    def __str__(self):
        return self.domain_slug

    def natural_key(self):
        return (self.domain_slug,)

    def get_domains(self):
        return self.objects.all().values_list('domain_slug')

    def get_by_natural_key(self, domain):
        return self.get(domain_slug=domain)
