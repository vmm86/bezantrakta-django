# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-08 12:49
from __future__ import unicode_literals

import bezantrakta.event.models.event_container_binder
import bezantrakta.event.models.event_link
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
            name='Event',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Всего не более 60-65 символов.', max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=64, verbose_name='Псевдоним')),
                ('description', models.TextField(help_text='Содержит ключевые слова или фразы, описывающие событие, но не более 3-5 шт.<br>Всего не более 150-200 символов.', max_length=200, verbose_name='Метатег `description`')),
                ('keywords', models.TextField(help_text='Несколько ключевых слов или фраз, разделённых запятыми, которые описывают событие.<br>Всего не более 100-150 символов.', max_length=150, verbose_name='Метатег `keywords`')),
                ('text', ckeditor.fields.RichTextField(verbose_name='Описание события')),
                ('is_published', models.BooleanField(default=False, verbose_name='Публикация')),
                ('is_on_index', models.BooleanField(default=False, verbose_name='На главной')),
                ('min_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Минимальная цена билета')),
                ('min_age', models.PositiveSmallIntegerField(choices=[(0, '0+'), (6, '6+'), (12, '12+'), (16, '16+'), (18, '18+')], default=0, verbose_name='Возрастное ограничение')),
                ('datetime', models.DateTimeField(verbose_name='Дата и время')),
                ('is_group', models.BooleanField(default=False, verbose_name='Группа')),
                ('ticket_service_event', models.PositiveIntegerField(blank=True, db_column='ticket_service_event_id', null=True, verbose_name='ID в сервисе продажи билетов')),
                ('ticket_service_prices', models.TextField(blank=True, max_length=200, null=True, verbose_name='Цены в сервисе продажи билетов')),
                ('ticket_service_scheme', models.PositiveIntegerField(blank=True, db_column='ticket_service_scheme_id', null=True, verbose_name='ID схемы зала в сервисе продажи билетов')),
                ('domain', models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт')),
            ],
            options={
                'verbose_name_plural': 'события или группы',
                'verbose_name': 'событие или группа',
                'db_table': 'bezantrakta_event',
                'ordering': ('domain', '-datetime', 'title', 'is_group'),
            },
        ),
        migrations.CreateModel(
            name='EventCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Всего не более 60-65 символов.', max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=64, unique=True, verbose_name='Псевдоним')),
                ('description', models.TextField(help_text='Содержит ключевые слова или фразы, описывающие категорию, но не более 3-5 шт.<br>Всего не более 150-200 символов.', max_length=200, verbose_name='Метатег `description`')),
                ('keywords', models.TextField(help_text='Несколько ключевых слов или фраз, разделённых запятыми, которые описывают категорию.<br>Всего не более 100-150 символов.', max_length=150, verbose_name='Метатег `keywords`')),
                ('is_published', models.BooleanField(default=True, verbose_name='Публикация')),
            ],
            options={
                'verbose_name': 'категория событий',
                'verbose_name_plural': 'категории событий',
                'db_table': 'bezantrakta_event_category',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='EventContainer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=64, verbose_name='Псевдоним')),
                ('mode', models.CharField(choices=[('big_vertical', 'Большие вертикальные'), ('big_horizontal', 'Большие горизонтальные'), ('small_vertical', 'Маленькие вертикальные'), ('small_horizontal', 'Маленькие горизонтальные')], db_index=True, default='small_vertical', max_length=16, verbose_name='Тип контейнера')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('img_width', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Ширина афиши')),
                ('img_height', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Высота афиши')),
                ('is_published', models.BooleanField(default=True, verbose_name='Публикация')),
            ],
            options={
                'verbose_name': 'контейнер',
                'verbose_name_plural': 'контейнеры',
                'db_table': 'bezantrakta_event_container',
                'ordering': ('order', 'is_published', 'title'),
            },
        ),
        migrations.CreateModel(
            name='EventContainerBinder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('order', models.PositiveSmallIntegerField(help_text='<div class="help"><strong>Афишу в позиции "маленькие вертикальные" нужно добавлять для всех событий</strong>, принадлежащих группе или независимых от групп! При отсутствии будет выводиться картинка-заглушка с логотипом Безантракта <img src="/static/global/ico/favicon.ico" width="16" height="16">.<br>"Маленькие вертикальные" афиши работают следующим образом:<ul><li>Если позиция <strong>равна 0</strong> – афиша НЕ выводится на главной, но используется для показа при фильтрации событий (по дате в календаре, категории, в поиске), а также для генерации электронных билетов.</li><li>Если позиция <strong>больше 1</strong> – афиши выводятся на главной при включении возможности показа на главной.</li><li>Если позиции афиш в контейнере <strong>больше 1 и одинаковые</strong> – афиши сортируются по дате/времени.</li></ul></div>', default=1, verbose_name='Порядок')),
                ('img', models.ImageField(blank=True, null=True, upload_to=bezantrakta.event.models.event_container_binder.img_path, verbose_name='Афиша')),
                ('event', models.ForeignKey(db_column='event_id', on_delete=django.db.models.deletion.CASCADE, to='event.Event', verbose_name='Событие')),
                ('event_container', models.ForeignKey(db_column='event_container_id', on_delete=django.db.models.deletion.CASCADE, to='event.EventContainer', verbose_name='Контейнер')),
            ],
            options={
                'verbose_name_plural': 'привязки к контейнерам',
                'verbose_name': 'привязка к контейнерам',
                'db_table': 'bezantrakta_event_container_binder',
                'ordering': ('order', 'event_container', 'event'),
            },
        ),
        migrations.CreateModel(
            name='EventGroupBinder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('caption', models.CharField(blank=True, help_text='<ul><li>Если событие в группе имеет особый статус, например, отдельные секторы зала в одном событии (танцпол, фанзона и т.п.). - указывается необходимое название.</li><li>Если это просто отдельные события в группе - оставляется пустым.</li></ul>', max_length=64, verbose_name='Подпись события в группе')),
                ('event', models.ForeignKey(db_column='event_id', on_delete=django.db.models.deletion.CASCADE, related_name='events', to='event.Event', verbose_name='Событие')),
                ('group', models.ForeignKey(db_column='group_id', on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='event.Event', verbose_name='Группа событий')),
            ],
            options={
                'verbose_name': 'привязка к группе событий',
                'verbose_name_plural': 'привязки к группе событий',
                'db_table': 'bezantrakta_event_group_binder',
                'ordering': ('group__datetime', 'event__datetime', 'caption'),
            },
        ),
        migrations.CreateModel(
            name='EventLink',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=32, verbose_name='Название')),
                ('slug', models.SlugField(max_length=32, verbose_name='Псевдоним')),
                ('img', models.ImageField(blank=True, help_text='Размер логотипа 192x64 px.', null=True, upload_to=bezantrakta.event.models.event_link.img_path, verbose_name='Логотип')),
            ],
            options={
                'verbose_name': 'ссылка',
                'verbose_name_plural': 'ссылки',
                'db_table': 'bezantrakta_event_link',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='EventLinkBinder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('href', models.URLField(blank=True, verbose_name='Внешняя ссылка')),
                ('order', models.PositiveSmallIntegerField(default=1, verbose_name='Порядок')),
                ('event', models.ForeignKey(db_column='event_id', on_delete=django.db.models.deletion.CASCADE, to='event.Event', verbose_name='Событие')),
                ('event_link', models.ForeignKey(db_column='event_link_id', on_delete=django.db.models.deletion.CASCADE, to='event.EventLink', verbose_name='Ссылка')),
            ],
            options={
                'verbose_name_plural': 'привязки к ссылкам',
                'verbose_name': 'привязка к ссылкам',
                'db_table': 'bezantrakta_event_link_binder',
                'ordering': ('order', 'event', 'event_link'),
            },
        ),
        migrations.CreateModel(
            name='EventVenue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(max_length=64, verbose_name='Псевдоним')),
                ('city', models.ForeignKey(db_column='city_id', on_delete=django.db.models.deletion.CASCADE, to='location.City', verbose_name='Город')),
            ],
            options={
                'verbose_name_plural': 'залы',
                'verbose_name': 'зал',
                'db_table': 'bezantrakta_event_venue',
                'ordering': ('city', 'title'),
            },
        ),
        migrations.AddField(
            model_name='event',
            name='event_category',
            field=models.ForeignKey(blank=True, db_column='event_category_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='event.EventCategory', verbose_name='Категория'),
        ),
        migrations.AddField(
            model_name='event',
            name='event_container',
            field=models.ManyToManyField(blank=True, related_name='event_containers', through='event.EventContainerBinder', to='event.EventContainer', verbose_name='Контейнеры, в которых отображается событие'),
        ),
        migrations.AddField(
            model_name='event',
            name='event_group',
            field=models.ManyToManyField(blank=True, related_name='event_groups', through='event.EventGroupBinder', to='event.Event', verbose_name='Группа, содержащая другие события'),
        ),
        migrations.AddField(
            model_name='event',
            name='event_link',
            field=models.ManyToManyField(blank=True, related_name='event_links', through='event.EventLinkBinder', to='event.EventLink', verbose_name='Ссылки, добавленные к событию'),
        ),
        migrations.AddField(
            model_name='event',
            name='event_venue',
            field=models.ForeignKey(blank=True, db_column='event_venue_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='event.EventVenue', verbose_name='Зал'),
        ),
    ]
