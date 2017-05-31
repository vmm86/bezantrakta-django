# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-23 14:56
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('domain', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Всего не более 60-65 символов', max_length=64, verbose_name='Название страницы')),
                ('slug', models.SlugField(max_length=64, verbose_name='Псевдоним страницы')),
                ('description', models.CharField(help_text='Должно сдержать ключевые слова или фразы,\n        описывающие событие, но не более 3-5 раз.\n\n        Всего не более 150-200 символов', max_length=64, verbose_name='Метатег `description`')),
                ('keywords', models.CharField(max_length=192, verbose_name='Метатег `keywords`')),
                ('text', ckeditor.fields.RichTextField(verbose_name='Содержимое страницы')),
                ('is_published', models.BooleanField(default=False, verbose_name='Опубликовано')),
                ('update_datetime', models.DateTimeField(auto_now=True, verbose_name='Сохранено')),
                ('domain', models.ForeignKey(blank=True, db_column='domain_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='domain.Domain', verbose_name='Домен')),
            ],
            options={
                'verbose_name': 'Страница',
                'verbose_name_plural': 'Страницы',
                'db_table': 'bezantrakta_article',
                'ordering': ('domain', 'title'),
            },
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['id'], name='bezantrakta_id_11f1ed_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('domain', 'slug')]),
        ),
    ]