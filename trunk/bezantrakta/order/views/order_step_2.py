import simplejson as json
import uuid
from collections import OrderedDict

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse

from project.cache import cache_factory
from project.shortcuts import build_absolute_url, message, render_messages

from bezantrakta.order.settings import ORDER_TYPE


def order_step_2(request):
    """Введение контактных данных покупателем и выбор типа заказа."""
    # Получение параметров события из cookie
    event_uuid = request.COOKIES.get('bezantrakta_event_uuid', uuid.uuid4())
    event_id = int(request.COOKIES.get('bezantrakta_event_id', 0))

    # Информация о событии из кэша
    event = cache_factory('event', event_uuid)
    if not event:
        # Сообщение об ошибке
        msgs = [
            message(
                'warning',
                'К сожалению, произошла ошибка предварительного резерва билетов. 🙁'
            ),
            message(
                'info',
                '👉 <a href="/">Начните поиск с главной страницы</a>.'
            ),
        ]
        render_messages(request, msgs)
        return redirect('error')

    # Информация о сервисе продажи билетов
    ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
    # Экземпляр класса сервиса продажи билетов
    ts = ticket_service['instance']

    # Информация о сервисе онлайн-оплаты
    payment_service = cache_factory('payment_service', event['payment_service_id'])
    # Экземпляр класса сервиса онлайн-оплаты, если она присутствует
    ps = payment_service['instance'] if payment_service else None

    # Получение реквизитов покупателя из предыдущего заказа (если он был)
    customer = {}
    customer['name'] = request.COOKIES.get('bezantrakta_customer_name', '')
    customer['phone'] = request.COOKIES.get('bezantrakta_customer_phone', '')
    customer['email'] = request.COOKIES.get('bezantrakta_customer_email', '')
    customer['address'] = request.COOKIES.get('bezantrakta_customer_address', request.city_title)
    customer['order_type'] = request.COOKIES.get('bezantrakta_customer_order_type', '')

    # Предварительный выбор типа заказа из списка активных,
    # если заказов ранее не было или если выбранный ранее тип заказа неактивен в конкретном событии

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
    if customer['order_type'] == '' or customer['order_type'] not in order_types_active:
        for ot in order_types.keys():
            if ot in order_types_active:
                customer['order_type'] = ot
                break

    # Информация о предварительном резерве и возможных опциях последующего заказа (УДАЛИТЬ!)
    order = {}
    order['uuid'] = request.COOKIES.get('bezantrakta_order_uuid')
    order['tickets'] = json.loads(request.COOKIES.get('bezantrakta_order_tickets', '[]'))
    order['tickets_count'] = int(request.COOKIES.get('bezantrakta_order_count', 0))
    order['total'] = ts.decimal_price(request.COOKIES.get('bezantrakta_order_total', 0))

    # Стоимость доставки курьером
    order['courier_price'] = ts.decimal_price(ticket_service['settings']['courier_price'])
    # Процент комиссии сервиса онлайн-оплаты, если он используется
    order['commission'] = (
        ps.decimal_price(payment_service['settings']['init']['commission']) if
        payment_service else
        ts.decimal_price(0)
    )

    # Формирование контекста для вывода в шаблоне
    context = {}

    context['event_uuid'] = event_uuid
    context['event_id'] = event_id

    context['event'] = event
    context['ticket_service'] = ticket_service
    context['payment_service'] = payment_service

    context['customer'] = customer

    context['order'] = order

    context['order_step_2_form_action'] = build_absolute_url(request.domain_slug, reverse('order:order_processing'))

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
