# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-13 13:07
from __future__ import unicode_literals

import bezantrakta.location.models.city
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='icon',
            field=models.ImageField(default='', upload_to=bezantrakta.location.models.city.img_path, verbose_name='Герб города'),
            preserve_default=False,
        ),
    ]
