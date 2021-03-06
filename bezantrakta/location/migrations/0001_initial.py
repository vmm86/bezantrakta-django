# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 12:49
from __future__ import unicode_literals

import bezantrakta.location.models.domain
from django.db import migrations, models
import django.db.models.deletion
import timezone_field.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.IntegerField(help_text='Идентификатор города - его телефонный код.', primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=8, verbose_name='Псевдоним')),
                ('timezone', timezone_field.fields.TimeZoneField(default='Europe/Moscow', verbose_name='Часовой пояс')),
                ('state', models.NullBooleanField(choices=[(False, 'отключен'), (None, 'подготовка'), (True, 'включен')], default=False, help_text='<ul><li>отключен - НЕ виден в списке городов и НЕ работает;</li><li>подготовка - виден в списке городов, но НЕ доступен для выбора (скоро открытие);</li><li>включен - виден в списке городов и работает.</li></ul>', verbose_name='Состояние')),
            ],
            options={
                'verbose_name': 'город',
                'verbose_name_plural': 'города',
                'db_table': 'bezantrakta_location_city',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.IntegerField(help_text='Идентификатор сайта - число из 3-х цифр.<br>Первые 2 цифры - автомобильный код региона, в котором находится город сайта.<br><a href="https://ru.wikipedia.org/wiki/Коды_субъектов_Российской_Федерации" target="_blank">👉 Поиск автомобильного кода региона</a><br>Третья цифра - порядковый номер от 0 до 9.', primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(help_text='<ul><li>Чтобы создать основной сайт в выбранном городе:<ul><li>псевдоним сайта должен совпадать с псевдонимом города,</li><li>последняя цифра идентификатора сайта - 0.</li></ul></li><li>Чтобы создать сайт какого-то учреждения в выбранном городе (например, ТОБ в Воронеже):<ul><li>псевдоним сайта может быть любым,</li><li>последняя цифра идентификатора сайта - от 1 до 9.</li></ul></li></ul>', max_length=8, verbose_name='Псевдоним')),
                ('is_published', models.BooleanField(default=False, help_text='<ul><li>опубликован - включен и работает;</li><li>НЕ опубликован - отключен (сайт недоступен, проводятся технические работы).</li></ul>', verbose_name='Публикация')),
                ('settings', models.TextField(default=bezantrakta.location.models.domain.default_json_settings_callable, verbose_name='Настройки в JSON')),
                ('city', models.ForeignKey(db_column='city_id', on_delete=django.db.models.deletion.CASCADE, to='location.City', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'сайт',
                'verbose_name_plural': 'сайты',
                'db_table': 'bezantrakta_location_domain',
                'ordering': ('city', 'title'),
            },
        ),
    ]
