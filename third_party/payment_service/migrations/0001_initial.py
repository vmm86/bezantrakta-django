# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 13:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentService',
            fields=[
                ('id', models.SlugField(max_length=32, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=32, verbose_name='Псевдоним')),
                ('is_active', models.BooleanField(default=False, verbose_name='Работает')),
                ('is_production', models.BooleanField(default=False, help_text='<ul><li>Если включено - оплата настоящими деньгами.</li><li>Если отключено - тестовая оплата НЕнастоящими деньгами.</li></ul>', verbose_name='Оплата настоящими деньгами')),
                ('settings', models.TextField(default='{}', verbose_name='Настройки')),
            ],
            options={
                'ordering': ('id', 'title'),
                'verbose_name': 'Сервис онлайн-оплаты',
                'verbose_name_plural': 'Сервисы онлайн-оплаты',
                'db_table': 'bezantrakta_payment_service',
            },
        ),
    ]
