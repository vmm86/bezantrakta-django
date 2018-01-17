import simplejson as json
import uuid
from collections import OrderedDict

from django.shortcuts import redirect, render

from project.cache import cache_factory
from project.shortcuts import build_absolute_url, message, render_messages

from bezantrakta.order.settings import ORDER_TYPE


def checkout(request):
    """Введение контактных данных покупателем и выбор типа заказа."""
    # Получение параметров события из cookie
    event_uuid = request.COOKIES.get('bezantrakta_event_uuid', uuid.uuid4())
    event_id = int(request.COOKIES.get('bezantrakta_event_id', 0))

    # Информация о событии из кэша
    event = cache_factory('event', event_uuid)
    if event is None:
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

    # Информация о сервисе продажи билетов и экземпляр класса сервиса продажи билетов
    ticket_service = cache_factory('ticket_service', event['ticket_service_id'])

    # Информация о сервисе онлайн-оплаты
    payment_service = cache_factory('payment_service', event['payment_service_id'])
    # Экземпляр класса сервиса онлайн-оплаты
    ps = payment_service['instance']

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
    customer['order_types_active'] = tuple(
        ot for ot in order_types.keys() if
        order_types[ot]['ticket_service'] is True and order_types[ot]['event'] is True
    )
    # Выбор первого доступного типа заказа по порядку,
    # если он НЕ был выбран ранее или если выбранный ранее тип заказа в текущем событии отключен
    if customer['order_type'] == '' or customer['order_type'] not in customer['order_types_active']:
        for ot in order_types.keys():
            if ot in customer['order_types_active']:
                customer['order_type'] = ot
                break

    # Информация о предварительном резерве и возможных опциях последующего заказа
    order = {}
    order['uuid'] = request.COOKIES.get('bezantrakta_order_uuid')
    order['tickets'] = json.loads(request.COOKIES.get('bezantrakta_order_tickets'))
    order['count'] = int(request.COOKIES.get('bezantrakta_order_count'))
    order['total'] = ps.decimal_price(request.COOKIES.get('bezantrakta_order_total'))

    # Стоимость доставки курьером
    order['courier_price'] = ps.decimal_price(ticket_service['settings']['courier_price'])
    # Процент комиссии сервиса онлайн-оплаты
    order['commission'] = ps.decimal_price(payment_service['settings']['init']['commission'])

    # Формирование контекста для вывода в шаблоне
    context = {}

    context['event_uuid'] = event_uuid
    context['event_id'] = event_id

    context['event'] = event
    context['ticket_service'] = ticket_service
    context['payment_service'] = payment_service

    context['customer'] = customer

    context['order'] = order

    context['checkout_form_action'] = build_absolute_url(request.domain_slug, '/afisha/order/')

    # Если корзина заказа пустая
    if order['count'] == 0:
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
        return render(request, 'order/checkout.html', context)
