# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 12:49
from __future__ import unicode_literals

import bezantrakta.banner.models
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
            name='BannerGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=32, verbose_name='Название')),
                ('slug', models.SlugField(max_length=32, verbose_name='Псевдоним')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'группа баннеров',
                'verbose_name_plural': 'группы баннеров',
                'db_table': 'bezantrakta_banner_group',
                'ordering': ('order', 'title'),
            },
        ),
        migrations.CreateModel(
            name='BannerGroupItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=32, verbose_name='Название')),
                ('slug', models.SlugField(max_length=32, verbose_name='Псевдоним')),
                ('img', models.ImageField(upload_to=bezantrakta.banner.models.img_path, verbose_name='Изображение баннера')),
                ('href', models.CharField(blank=True, max_length=128, verbose_name='Ссылка')),
                ('is_published', models.BooleanField(default=False, verbose_name='Публикация')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('banner_group', models.ForeignKey(db_column='banner_group_id', on_delete=django.db.models.deletion.CASCADE, to='banner.BannerGroup', verbose_name='Группа баннеров')),
                ('domain', models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт')),
            ],
            options={
                'verbose_name_plural': 'баннеры',
                'verbose_name': 'баннер',
                'db_table': 'bezantrakta_banner_group_item',
                'ordering': ('order', 'banner_group', 'domain', 'title'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='bannergroupitem',
            unique_together=set([('domain', 'banner_group', 'slug')]),
        ),
    ]
