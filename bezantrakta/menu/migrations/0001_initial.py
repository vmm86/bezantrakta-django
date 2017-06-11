# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-11 15:01
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
                'ordering': ('order', 'title'),
                'db_table': 'bezantrakta_menu',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(blank=True, help_text='Псевдоним пункта меню должен совпадать\n        с псевдонимом страницы, которую требуется в нём отобразить.', max_length=64, verbose_name='Псевдоним')),
                ('is_published', models.BooleanField(default=False, verbose_name='Публикация')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Порядок в меню')),
                ('domain', models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Домен')),
                ('menu', models.ForeignKey(db_column='menu_id', on_delete=django.db.models.deletion.CASCADE, to='menu.Menu', verbose_name='Меню')),
            ],
            options={
                'db_table': 'bezantrakta_menu_item',
                'verbose_name': 'пункт меню',
                'ordering': ('order', 'domain', 'menu', 'title'),
                'verbose_name_plural': 'пункты меню',
            },
        ),
        migrations.AlterUniqueTogether(
            name='menuitem',
            unique_together=set([('domain', 'menu', 'slug')]),
        ),
    ]
