# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-02 08:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='is_published',
            field=models.BooleanField(default=False, help_text='\n        True - включен и работает,\n        False - отключен (скоро открытие).', verbose_name='Публикация'),
        ),
    ]