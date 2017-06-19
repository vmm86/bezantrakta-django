# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-19 11:00
from __future__ import unicode_literals

import bezantrakta.event.models.link
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0004_auto_20170614_0856'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventcontainerbinder',
            options={'ordering': ('order', 'event', 'event_container'), 'verbose_name': 'связка событий и контейнеров', 'verbose_name_plural': 'связки событий и контейнеров'},
        ),
        migrations.AlterModelOptions(
            name='eventlinkbinder',
            options={'ordering': ('order', 'event', 'event_link'), 'verbose_name': 'связка событий и ссылок', 'verbose_name_plural': 'связки событий и ссылок'},
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='description',
            field=models.TextField(default='', help_text='Содержит ключевые слова или фразы, описывающие группу, но не более 3-5 шт.<br>Всего не более 150-200 символов.', max_length=200, verbose_name='Метатег `description`'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventgroup',
            name='keywords',
            field=models.TextField(default='', help_text='Несколько ключевых слов или фраз, разделённых запятыми, которые описывают группу.<br>Всего не более 100-150 символов.', max_length=150, verbose_name='Метатег `keywords`'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(help_text='Содержит ключевые слова или фразы, описывающие событие, но не более 3-5 шт.<br>Всего не более 150-200 символов.', max_length=200, verbose_name='Метатег `description`'),
        ),
        migrations.AlterField(
            model_name='event',
            name='domain',
            field=models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт'),
        ),
        migrations.AlterField(
            model_name='event',
            name='keywords',
            field=models.TextField(help_text='Несколько ключевых слов или фраз, разделённых запятыми, которые описывают событие.<br>Всего не более 100-150 символов.', max_length=150, verbose_name='Метатег `keywords`'),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(help_text='Всего не более 60-65 символов.', max_length=64, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='description',
            field=models.CharField(help_text='Содержит ключевые слова или фразы, описывающие категорию, но не более 3-5 шт.<br>Всего не более 150-200 символов.', max_length=200, verbose_name='Метатег `description`'),
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='keywords',
            field=models.CharField(help_text='Несколько ключевых слов или фраз, разделённых запятыми, которые описывают категорию.<br>Всего не более 100-150 символов.', max_length=150, verbose_name='Метатег `keywords`'),
        ),
        migrations.AlterField(
            model_name='eventcategory',
            name='title',
            field=models.CharField(help_text='Всего не более 60-65 символов.', max_length=64, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='eventcontainerbinder',
            name='event_container',
            field=models.ForeignKey(db_column='event_container_id', on_delete=django.db.models.deletion.CASCADE, to='event.EventContainer', verbose_name='Контейнер'),
        ),
        migrations.AlterField(
            model_name='eventgroup',
            name='domain',
            field=models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт'),
        ),
        migrations.AlterField(
            model_name='eventgroup',
            name='title',
            field=models.CharField(help_text='Всего не более 60-65 символов.', max_length=64, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='eventlink',
            name='img',
            field=models.ImageField(blank=True, help_text='Размер логотипа 192x64 px.', null=True, upload_to=bezantrakta.event.models.link.img_path, verbose_name='Логотип'),
        ),
        migrations.AlterField(
            model_name='eventlinkbinder',
            name='event_link',
            field=models.ForeignKey(db_column='event_link_id', on_delete=django.db.models.deletion.CASCADE, to='event.EventLink', verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='eventvenue',
            name='domain',
            field=models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт'),
        ),
        migrations.AlterField(
            model_name='eventvenue',
            name='title',
            field=models.CharField(max_length=64, verbose_name='Название'),
        ),
    ]
