# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-01 09:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0006_auto_20170524_1256'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domain',
            old_name='is_online',
            new_name='is_published',
        ),
    ]
