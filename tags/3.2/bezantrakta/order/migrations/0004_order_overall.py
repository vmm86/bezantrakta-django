# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-12 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_remove_orderticket_price_group_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='overall',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Всего'),
            preserve_default=False,
        ),
    ]
