# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 12:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('location', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=32, verbose_name='Псевдоним')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'меню',
                'verbose_name_plural': 'меню',
                'db_table': 'bezantrakta_menu',
                'ordering': ('order', 'title'),
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.CharField(blank=True, max_length=128, verbose_name='Ссылка')),
                ('is_published', models.BooleanField(default=False, verbose_name='Публикация')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('domain', models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт')),
                ('menu', models.ForeignKey(db_column='menu_id', on_delete=django.db.models.deletion.CASCADE, to='menu.Menu', verbose_name='Меню')),
            ],
            options={
                'verbose_name_plural': 'пункты меню',
                'verbose_name': 'пункт меню',
                'db_table': 'bezantrakta_menu_item',
                'ordering': ('order', 'domain', 'menu', 'title'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='menuitem',
            unique_together=set([('domain', 'menu', 'slug')]),
        ),
    ]