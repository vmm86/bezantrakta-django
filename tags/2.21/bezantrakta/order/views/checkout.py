import simplejson as json
import uuid

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
    # Экземпляр класса сервиса продажи билетов
    ts = ticket_service['instance']

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

    # Предварительный выбор типа заказа из списка активных, если заказов ранее не было
    order_types_active = [k for k, v in ticket_service['settings']['order'].items() if v == True]
    if customer['order_type'] == '' or customer['order_type'] not in order_types_active:
        for ot in ORDER_TYPE:
            if ot in order_types_active:
                customer['order_type'] = ot
                break

    # Получение параметров заказа из cookie
    order_uuid = request.COOKIES.get('bezantrakta_order_uuid')
    order_tickets = json.loads(request.COOKIES.get('bezantrakta_order_tickets'))
    order_count = int(request.COOKIES.get('bezantrakta_order_count'))
    order_total = ts.decimal_price(request.COOKIES.get('bezantrakta_order_total'))

    # Стоимость доставки курьером
    courier_price = ts.decimal_price(ticket_service['settings']['courier_price'])
    # Общая сумма заказа со стоимостью доставки курьером
    order_total_plus_courier_price = order_total + courier_price

    # Комиссия сервиса онлайн-оплаты
    commission = ps.decimal_price(payment_service['settings']['init']['commission'])
    # Общая сумма заказа с комиссией сервиса онлайн-оплаты
    order_total_plus_commission = ps.total_plus_commission(order_total)

    # Формирование контекста для вывода в шаблоне
    context = {}

    context['event_uuid'] = event_uuid
    context['event_id'] = event_id

    context['event'] = event
    context['ticket_service'] = ticket_service
    context['payment_service'] = payment_service

    context['customer'] = customer

    context['order_types_active'] = order_types_active

    context['order_uuid'] = order_uuid
    context['order_tickets'] = order_tickets
    context['order_count'] = order_count
    context['order_total'] = order_total

    context['courier_price'] = str(courier_price)
    context['order_total_plus_courier_price'] = str(order_total_plus_courier_price)

    context['commission'] = str(commission)
    context['order_total_plus_commission'] = str(order_total_plus_commission)

    context['checkout_form_action'] = build_absolute_url(request.domain_slug, '/afisha/order/')

    # Если корзина заказа пустая
    if context['order_count'] == 0:
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
