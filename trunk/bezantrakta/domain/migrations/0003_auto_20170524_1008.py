# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-24 10:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0002_auto_20170524_1007'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='domain',
            name='bezantrakta_id_0d1f3d_idx',
        ),
    ]
