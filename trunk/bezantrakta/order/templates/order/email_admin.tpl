{% extends "mail_templated/base.tpl" %}

{% block subject %}
{{ domain.title }}: {% if order.order_id %}Заказ № {{ order.order_id }}{% else %}Заказ{% endif %} ({{ customer.delivery_description }}, {{ customer.payment_description }})
{% endblock %}

{% block html %}
{% spaceless %}
<!DOCTYPE html>
<html style="width: 100%; height: 100%;">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="format-detection" contant="telephone=no">
</head>
<body bgcolor="ffffff" topmargin="10" leftmargin="10" marginwidth="10" marginheight="10" offset="0">

    <h2>{{ domain.title }}: {% if order.order_id %}Заказ № &#8203;{{ order.order_id }}{% else %}Заказ{% endif %}</h2>

    <h3>{{ event.event_date }} {{ event.event_title }}</h3>
    <h3>{{ event.event_venue_title }}</h3>

    <p><strong>Билеты в заказе</strong>:</p>
    <ul style="list-style-type: none; margin-left: 0; padding-left: 0;">
    {% for t in order.tickets %}
        <li style="margin-left: 0; padding-left: 0;">🎫 {{ t.sector_title }}, ряд {{ t.row_id }}, место {{ t.seat_title }}, цена {{ t.price }} р.</li>
    {% endfor %}
    </ul>

    <p><strong>Общая сумма заказа</strong>: {{ order.total }} р.
    {% if customer.delivery == "courier" and ticket_service.settings.courier_price > 0 %}
        <br>В сумму заказа включена стоимость доставки курьером.
    {% endif %}
    {% if customer.payment == "online" and payment_service.settings.commission > 0 %}
        <br>К сумме заказа добавлена комиссия сервиса онлайн-оплаты.
    {% endif %}
    </p>

    <p><strong>Реквизиты покупателя</strong>:</p>
    <p>
        <strong>Имя</strong>: {{ customer.name }}.
        <br>
        <strong>Email</strong>: <a href="mailto:{{ customer.email }}">{{ customer.email }}</a>.
        <br>
        <strong>Телефон</strong>: <a href="tel:{{ customer.phone|cut:" "|cut:"-"|cut:"("|cut:")" }}">{{ customer.phone }}</a>.
    </p>

    <p><strong>Получение билетов</strong>: {{ customer.delivery_description }}.
    {% if customer.delivery == "courier" %}
        <br><strong>Адрес доставки</strong>: {% if customer.address or customer.address != "" %}{{ customer.address }}{% else %}не указан{% endif %}.
    {% endif %}
    </p>

    <p><strong>Оплата</strong>: {{ customer.payment_description }}.
    {% if customer.payment == "online" %}
        <br><strong>Номер оплаты</strong>: {{ order.payment_id }}.
    {% endif %}
    </p>

    <p><strong>Статус заказа</strong>: <strong style="color: {{ customer.status_color }}">{{ customer.status_description }}</strong>.</p>

</body>
{% endspaceless %}
{% endblock %}
