from django.conf.urls import url

from .views import checkout, order, confirmation

app_name = 'order'

urlpatterns = [
    # Шаг 2 заказа билетов (ввод контактов покупателя и выбор способа доставки и оплаты билетов)
    url(
        r'^afisha/checkout/$',
        checkout,
        name='checkout'
    ),
    # Оформление заказа после отправки формы на шаге 2 заказа билетов
    # Завершение заказа для оплаты наличными либо редирект на запрошенную форму онлайн-оплаты
    url(
        r'^afisha/order/$',
        order,
        name='order'
    ),
    # Шаг 3 заказа билетов (подтверждение успешного заказа с краткой информацией о нём)
    url(
        r'^afisha/order/(?P<order_uuid>[0-9A-Fa-f\-]+)/$',
        confirmation,
        name='confirmation'
    ),
]
