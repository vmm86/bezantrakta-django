# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-29 08:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banner', '0006_auto_20170529_0851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannergroupitem',
            name='order',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Порядок'),
        ),
    ]