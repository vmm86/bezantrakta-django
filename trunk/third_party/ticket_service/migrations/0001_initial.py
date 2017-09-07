# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-07 13:17
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('event', '0001_initial'),
        ('location', '0001_initial'),
        ('payment_service', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketService',
            fields=[
                ('id', models.SlugField(max_length=32, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('title', models.CharField(max_length=64, verbose_name='Название')),
                ('slug', models.SlugField(help_text='<p>Псевдоним должен совпадать с атрибутом <strong>slug</strong> класса соответствующего билетного сервиса.</p><p><ul><li><strong>superbilet</strong> для СуперБилет,</li><li><strong>radario</strong> для Радарио.</li></ul></p>', max_length=32, verbose_name='Псевдоним')),
                ('is_active', models.BooleanField(default=False, verbose_name='Работает')),
                ('settings', models.TextField(default='{}', verbose_name='Настройки в JSON')),
                ('domain', models.ForeignKey(db_column='domain_id', on_delete=django.db.models.deletion.CASCADE, to='location.Domain', verbose_name='Сайт')),
            ],
            options={
                'ordering': ('slug', 'title'),
                'verbose_name': 'Сервис продажи билетов',
                'verbose_name_plural': 'Сервисы продажи билетов',
                'db_table': 'bezantrakta_ticket_service',
            },
        ),
        migrations.CreateModel(
            name='TicketServiceVenueBinder',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ticket_service_event_venue_id', models.PositiveIntegerField(verbose_name='ID схемы в сервисе продажи билетов')),
                ('ticket_service_event_venue_title', models.CharField(max_length=128, verbose_name='Название схемы в сервисе продажи билетов')),
                ('scheme', ckeditor.fields.RichTextField(default='', help_text='<p>Схема зала в HTML, как правило, на основе таблиц. Возможно использование SVG в тех случаях, когда это необходимо.</p><p>У родительского элемента всей схемы зала (&lt;table&gt; или &lt;svg&gt;) указывается класс <strong>stagehall</strong>.</p><p>Специфическим элементам схемы зала указываются соответствующие классы:</p><ul><li><strong>stage</strong> - сцена,</li><li><strong>sector</strong> - название сектора или номер ряда,</li><li><strong>seat</strong> - кликабельное место, которое также содержит data-атрибуты места из схемы в сервисе продажи билетов:<ul><li><strong>data-sector-id</strong> - идентификатор сектора,</li><li><strong>data-row-id</strong> - идентификатор ряда,</li><li><strong>data-seat-id</strong> - идентификатор места.</li></ul></li></ul><p>Остальные data-атрибуты подгружаются к каждому доступному для заказа месту при обновлении схемы зала на 1-м шаге заказа билетов.</p>', verbose_name='Схема зала')),
                ('event_venue', models.ForeignKey(blank=True, db_column='event_venue_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='event.EventVenue', verbose_name='Зал')),
                ('ticket_service', models.ForeignKey(db_column='ticket_service_id', on_delete=django.db.models.deletion.CASCADE, to='ticket_service.TicketService', verbose_name='Сервис продажи билетов')),
            ],
            options={
                'db_table': 'bezantrakta_ticket_service_venue_binder',
                'verbose_name_plural': 'Связки сервисов продажи билетов и схем залов',
                'ordering': ('ticket_service', 'ticket_service_event_venue_id', 'event_venue'),
                'verbose_name': 'Связка сервисов продажи билетов и схем залов',
            },
        ),
        migrations.AddField(
            model_name='ticketservice',
            name='event_venue',
            field=models.ManyToManyField(blank=True, related_name='ticket_service_venues', through='ticket_service.TicketServiceVenueBinder', to='event.EventVenue', verbose_name='Зал'),
        ),
        migrations.AddField(
            model_name='ticketservice',
            name='payment_service',
            field=models.ForeignKey(blank=True, db_column='payment_service_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='payment_service.PaymentService', verbose_name='Сервис онлайн-оплаты'),
        ),
        migrations.AlterUniqueTogether(
            name='ticketservicevenuebinder',
            unique_together=set([('ticket_service', 'ticket_service_event_venue_id')]),
        ),
    ]
