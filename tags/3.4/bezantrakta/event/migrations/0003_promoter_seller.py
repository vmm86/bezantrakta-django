# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-26 09:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_auto'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='promoter',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Организатор'),
        ),
        migrations.AddField(
            model_name='event',
            name='seller',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Агент'),
        ),
    ]