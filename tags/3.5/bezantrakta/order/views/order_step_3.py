import uuid

from django.conf import settings
from django.shortcuts import redirect, render

from project.cache import cache_factory
from project.shortcuts import message, render_messages

from ..order_basket import OrderBasket


def order_step_3(request, order_uuid):
    """Вывод информации об успешном или НЕуспешном заказе.

    Args:
        order_uuid (str): Уникальный идентификатор заказа.
    """
    try:
        order_uuid = uuid.UUID(order_uuid)
    except (TypeError, ValueError):
        order_uuid = None

    # Сообщение об ошибке
    if not order_uuid:
        msgs = [
            message('error', 'К сожалению, произошла ошибка - такого заказа не существует. 🙁'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')

    basket = OrderBasket(order_uuid=order_uuid, logger='bezantrakta.order')
    if not basket or not basket.order:
        # Сообщение об ошибке
        msgs = [
            message('error', 'Предварительный резерв некорректен или отсутствует. 🙁'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')

    # Информация о событии из кэша
    event = cache_factory('event', basket.order['event_uuid'])

    # Вывод основной информации о заказе
    order_info = []
    order_info.append({'key': 'Номер заказа:', 'value': basket.order['order_id']})

    order_info.append({
        'key': 'Статус заказа:',
        'value': '<span style="color: {color};">{description}</span>'.format(
            color=basket.order['status_color'],
            description=basket.order['status_caption'],
        )
    })
    order_info.append({'key': 'Получение:', 'value': basket.order['delivery_caption']})
    if basket.order['delivery'] == 'courier':
        order_info.append({'key': 'Адрес доставки:', 'value': basket.order['customer']['address']})
    order_info.append({'key': 'Оплата:',    'value': basket.order['payment_caption']})

    if basket.order['payment'] == 'online' and basket.order['status'] == 'approved':
        order_info.append({'key': 'Номер оплаты:', 'value': basket.order['payment_id']})

    context = {}

    context['event'] = event
    context['order'] = basket.order
    context['order_info'] = order_info

    basket.delete()

    # Разрешён ли вывод отладочной информации в консоли браузера
    cookie_debugger = request.COOKIES.get(settings.BEZANTRAKTA_COOKIE_WATCHER_TITLE, None)
    context['watcher'] = True if cookie_debugger == settings.BEZANTRAKTA_COOKIE_WATCHER_VALUE else False

    return render(request, 'order/order_step_3.html', context)
