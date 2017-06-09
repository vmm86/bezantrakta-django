# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-02 08:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_city_is_published'),
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('domain', 'slug', 'is_published')]),
        ),
    ]