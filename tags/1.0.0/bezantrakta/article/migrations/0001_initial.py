# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-19 11:49
from __future__ import unicode_literals

import ckeditor.fields
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
            name='Article',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Всего не более 60-65 символов.', max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=64, verbose_name='Псевдоним')),
                ('description', models.TextField(help_text='Содержит ключевые слова или фразы, описывающие страницу, но не более 3-5 шт.<br>Всего не более 150-200 символов.', max_length=200, verbose_name='Метатег `description`')),
                ('keywords', models.TextField(help_text='Несколько ключевых слов или фраз, разделённых запятыми, которые описывают содержимое страницы.<br>Всего не более 100-150 символов.', max_length=150, verbose_name='Метатег `keywords`')),
                ('text', ckeditor.fields.RichTextField(verbose_name='Содержимое страницы')),
                ('is_published', models.BooleanField(default=False, verbose_name='Публикация')),
                ('domain', models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт')),
            ],
            options={
                'verbose_name': 'HTML-страница',
                'db_table': 'bezantrakta_article',
                'ordering': ('domain', 'title', 'is_published'),
                'verbose_name_plural': 'HTML-страницы',
            },
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('domain', 'slug')]),
        ),
    ]