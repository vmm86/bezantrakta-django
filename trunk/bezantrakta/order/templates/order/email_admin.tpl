{% extends "mail_templated/base.tpl" %}

{% block subject %}
{{ domain.domain_title }}: {% if order.order_id %}Заказ № {{ order.order_id }}{% else %}Заказ{% endif %} ({{ order.delivery_caption }}, {{ order.payment_caption }})
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

    <h2>{{ domain.domain_title }}: {% if order.order_id %}Заказ № &#8203;{{ order.order_id }}{% else %}Заказ{% endif %}</h2>

    <h3>{{ event.event_date }} {{ event.event_time }} {{ event.event_title }}</h3>
    <h3>{{ event.event_venue_title }} {% if event.event_venue_city %}({{ event.event_venue_city }}){% endif %}</h3>

    <p><strong>Билеты в заказе</strong>:</p>
    <ul style="list-style-type: none; margin-left: 0; padding-left: 0;">
    {% for tid, t in order.tickets.items %}
        <li style="margin-left: 0; padding-left: 0;">🎫 {% if t.is_fixed %}{{ t.sector_title }}, ряд {{ t.row_id }}, место {{ t.seat_title }}{% else %}{{ t.sector_title }}{% endif %}, цена {{ t.price|floatformat:"-2" }} р.</li>
    {% endfor %}
    </ul>

    <p><strong>Общая сумма заказа</strong>: {{ order.overall|floatformat:"-2" }} р.
    {% if order.overall != order.total %}
        <br>{{ order.overall_header }}.
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

    <p><strong>Получение билетов</strong>: {{ order.delivery_caption }}.
    {% if customer.delivery == "courier" %}
        <br><strong>Адрес доставки</strong>: {% if customer.address or customer.address != "" %}{{ customer.address }}{% else %}не указан{% endif %}.
    {% endif %}
    </p>

    <p><strong>Оплата</strong>: {{ order.payment_caption }}.
    {% if customer.payment == "online" %}
        <br><strong>Номер оплаты</strong>: {{ order.payment_id }}.
    {% endif %}
    </p>

    <p><strong>Статус заказа</strong>: <strong style="color: {{ order.status_color }}">{{ order.status_caption }}</strong>.</p>

</body>
{% endspaceless %}
{% endblock %}
