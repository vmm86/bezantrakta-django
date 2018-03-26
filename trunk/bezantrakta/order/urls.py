from django.conf.urls import url

from .views import order_step_1, order_step_2, order_step_3, download_pdf_ticket

app_name = 'order'

urlpatterns = [
    # Шаг 1 заказа билетов (страница события и выбор билетов на схеме зала)
    url(
        r'^afisha/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)-(?P<minute>\d+)/(?P<slug>[\w-]+)/$',
        order_step_1,
        name='order_step_1'
    ),

    # Шаг 2 заказа билетов (ввод контактов покупателя и выбор способа доставки/оплаты билетов)
    url(
        r'^afisha/checkout/$',
        order_step_2,
        name='order_step_2'
    ),
    # Шаг 3 заказа билетов (подтверждение успешного заказа с информацией о нём)
    url(
        r'^afisha/order/(?P<order_uuid>[0-9A-f-]+)/$',
        order_step_3,
        name='order_step_3'
    ),

    # Скачать PDF-билет
    url(
        r'^afisha/domain/(?P<domain_slug>[A-z-]+)/order/(?P<order_id>[0-9-]+)/pdf_ticket/(?P<ticket_uuid>[0-9A-f-]+)/$',
        download_pdf_ticket,
        name='download_pdf_ticket'
    ),
]
