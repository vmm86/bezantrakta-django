# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-23 14:56
from __future__ import unicode_literals

import bezantrakta.domain.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('city', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50, verbose_name='Название домена')),
                ('slug', models.SlugField(max_length=100, unique=True, validators=[bezantrakta.domain.models._domain_name_validator], verbose_name='Псевдоним домена')),
                ('city', models.ForeignKey(db_column='city_id', on_delete=django.db.models.deletion.CASCADE, to='city.City', verbose_name='Город')),
            ],
            options={
                'verbose_name_plural': 'Домены',
                'db_table': 'bezantrakta_domain',
                'ordering': ('city', 'title'),
                'verbose_name': 'Домен',
            },
        ),
        migrations.AddIndex(
            model_name='domain',
            index=models.Index(fields=['id'], name='bezantrakta_id_0d1f3d_idx'),
        ),
    ]