from django.conf.urls import url

from .views import order_step_1, order_step_2, order_processing, order_step_3

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
    # Обработка заказа после отправки формы на шаге 2 заказа билетов
    # Завершение заказа для оплаты наличными либо редирект на запрошенную форму онлайн-оплаты
    url(
        r'^afisha/order/$',
        order_processing,
        name='order_processing'
    ),
    # Шаг 3 заказа билетов (подтверждение успешного заказа с информацией о нём)
    url(
        r'^afisha/order/(?P<order_uuid>[0-9A-Fa-f\-]+)/$',
        order_step_3,
        name='order_step_3'
    ),
]
