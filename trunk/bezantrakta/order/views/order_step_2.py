import uuid
from collections import OrderedDict

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse

from project.cache import cache_factory
from project.shortcuts import build_absolute_url, message, render_messages

from bezantrakta.order.order_basket import OrderBasket
from bezantrakta.order.settings import ORDER_TYPE


def order_step_2(request):
    """Введение реквизитов покупателем и выбор типа заказа."""
    # UUID события
    event_uuid = request.COOKIES.get('bezantrakta_event_uuid', None)
    try:
        event_uuid = uuid.UUID(event_uuid)
    except (TypeError, ValueError):
        redirect('/')

    # UUID предварительного резерва
    order_uuid = request.COOKIES.get('bezantrakta_order_uuid', None)
    try:
        order_uuid = uuid.UUID(order_uuid)
    except (TypeError, ValueError):
        redirect('/')

    # Информация о событии из кэша
    event = cache_factory('event', event_uuid)
    if not event:
        redirect('/')

    # Получение параметров сайта
    domain = cache_factory('domain', request.domain_slug)

    # Информация о сервисе продажи билетов
    ticket_service = cache_factory('ticket_service', event['ticket_service_id'])

    # Информация о сервисе онлайн-оплаты
    payment_service = cache_factory('payment_service', event['payment_service_id'])

    # Предварительный выбор типа заказа из списка активных,
    # если заказов ранее не было или если выбранный ранее тип заказа неактивен в конкретном событии

    # Получение типа заказа из предыдущего заказа (если он был сделан ранее)
    order_type = request.COOKIES.get('bezantrakta_customer_order_type', None)
    default_order_type = None

    # Все типы заказа билетов для выбора (настройки в сервисе продажи билетов и в событии)
    order_types = OrderedDict()
    for ot in ORDER_TYPE:
        order_types.update(
            {
                ot: {
                    'ticket_service': ticket_service['settings']['order'][ot],
                    'event':                   event['settings']['order'][ot],
                }
            }
        )

    # Активные типы заказа билетов в конкретном событии
    order_types_active = tuple(
        ot for ot in order_types.keys() if
        order_types[ot]['ticket_service'] is True and order_types[ot]['event'] is True and
        (payment_service or not ot.endswith('_online'))
    )
    # Типы заказа билетов с онлайн-оплатой НЕ включаются в список активных,
    # если к текущему сервису продажи билетов НЕ привязан никакой сервис онлайн-оплаты

    # Выбор первого доступного типа заказа по порядку,
    # если он НЕ был выбран ранее или если выбранный ранее тип заказа в текущем событии отключен
    if not order_type or order_type not in order_types_active:
        for ot in order_types.keys():
            if ot in order_types_active:
                default_order_type = ot
                break
    else:
        default_order_type = order_type

    # Получение существующего предварительного резерва
    basket = OrderBasket(order_uuid=order_uuid)
    order = basket.order

    if not order:
        redirect('/')

    # Формирование контекста для вывода в шаблоне
    context = {}

    context['domain'] = domain

    context['event_uuid'] = event_uuid

    context['event'] = event
    context['ticket_service'] = ticket_service
    context['payment_service'] = payment_service

    context['order'] = order
    context['default_order_type'] = default_order_type
    context['form_action'] = build_absolute_url(request.domain_slug, reverse('order:order_processing'))

    # Разрешён ли вывод отладочной информации в консоли браузера
    cookie_debugger = request.COOKIES.get(settings.BEZANTRAKTA_COOKIE_WATCHER_TITLE, None)
    context['watcher'] = True if cookie_debugger == settings.BEZANTRAKTA_COOKIE_WATCHER_VALUE else False

    # Если корзина заказа пустая
    if order['tickets_count'] == 0:
        # Сообщение об ошибке
        msgs = [
            message(
                'warning',
                'К сожалению, вы не добавили билеты в предварительный резерв либо время его действия истекло. 🙁'
            ),
            message(
                'info',
                '👉 <a href="{url}">Выбирайте нужные Вам билеты и оформляйте заказ</a>.'.format(url=event['url'])
            ),
        ]
        render_messages(request, msgs)
        return redirect('error')
    # Если корзина заказа НЕпустая
    else:
        return render(request, 'order/order_step_2.html', context)
