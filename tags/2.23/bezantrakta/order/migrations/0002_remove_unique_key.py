# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-17 20:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='orderticket',
            unique_together=set([]),
        ),
    ]