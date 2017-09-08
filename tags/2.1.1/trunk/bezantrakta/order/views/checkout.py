import simplejson as json

from django.conf import settings
from django.shortcuts import redirect, render

from project.shortcuts import message, render_messages

from bezantrakta.event.cache import get_or_set_cache as get_or_set_event_cache

from third_party.payment_service.cache import get_or_set_cache as get_or_set_payment_service_cache
from third_party.payment_service.cache import payment_service_instance

from third_party.ticket_service.cache import get_or_set_cache as get_or_set_ticket_service_cache
from third_party.ticket_service.cache import ticket_service_instance


def checkout(request):
    """Введение контактных данных покупателем и выбор типа заказа."""
    # Получение параметров события из cookie
    event_uuid = request.COOKIES.get('bezantrakta_event_uuid')
    event_id = int(request.COOKIES.get('bezantrakta_event_id'))

    # Информация о событии из кэша
    event = get_or_set_event_cache(event_uuid)

    # Информация о сервисе продажи билетов
    ticket_service = get_or_set_ticket_service_cache(event['ticket_service_id'])

    # Проверка настроек, которые при отсутствии значений выставляются по умолчанию
    ticket_service_defaults = {
        # Таймаут для повторения запроса списка мест в событии в секундах
        'heartbeat_timeout': settings.BEZANTRAKTA_DEFAULT_HEARTBEAT_TIMEOUT,
        # Таймаут для выделения места в минутах, по истечении которого место автоматически освобождается
        'seat_timeout': settings.BEZANTRAKTA_DEFAULT_SEAT_TIMEOUT,
    }
    for param, value in ticket_service_defaults.items():
        if param not in ticket_service['settings'] or ticket_service['settings'][param] is None:
            ticket_service['settings'][param] = value

    # Информация о сервисе онлайн-оплаты
    payment_service = get_or_set_payment_service_cache(event['payment_service_id'])

    # Экземпляр класса сервиса продажи билетов
    ts = ticket_service_instance(event['ticket_service_id'])
    # Экземпляр класса сервиса онлайн-оплаты
    ps = payment_service_instance(event['payment_service_id'])

    # Получение реквизитов покупателя из предыдущего заказа (если он был)
    customer = {}
    customer['name'] = request.COOKIES.get('bezantrakta_customer_name', '')
    customer['phone'] = request.COOKIES.get('bezantrakta_customer_phone', '')
    customer['email'] = request.COOKIES.get('bezantrakta_customer_email', '')
    customer['address'] = request.COOKIES.get('bezantrakta_customer_address', request.city_title)
    customer['order_type'] = request.COOKIES.get('bezantrakta_customer_order_type', '')

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

    context['order_uuid'] = order_uuid
    context['order_tickets'] = order_tickets
    context['order_count'] = order_count
    context['order_total'] = order_total

    context['courier_price'] = str(courier_price)
    context['order_total_plus_courier_price'] = str(order_total_plus_courier_price)

    context['commission'] = commission
    context['order_total_plus_commission'] = str(order_total_plus_commission)

    # Если корзина заказа пустая
    if context['order_count'] == 0:
        # Сообщение об ошибке
        msgs = [
            message(
                'warning',
                'К сожалению, вы ещё не забронировали ни одного места либо ваша бронь истекла. 😞'
            ),
            message(
                'info',
                '👉 <a href="javascript: history.go(-1)">Выбирайте нужные Вам билеты и оформляйте заказ</a>.'
            ),
        ]
        render_messages(request, msgs)
        return redirect('error')
    # Если корзина заказа НЕпустая
    else:
        return render(request, 'order/checkout.html', context)
