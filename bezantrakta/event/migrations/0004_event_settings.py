# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-15 09:26
from __future__ import unicode_literals

import bezantrakta.event.models.event
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0003_promoter_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='settings',
            field=models.TextField(default=bezantrakta.event.models.event.default_json_settings_callable, verbose_name='Настройки в JSON'),
        ),
    ]
