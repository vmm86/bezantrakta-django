from project.cache import cache_factory

from bezantrakta.order.settings import ORDER_TYPE


def order_info(request, event, order):
    """Заготовка для работы с заказаом на сервере при получении AJAX-запроса от клиента.

    Args:
        event (TYPE): Информация о событии.
        order (TYPE): Информация о заказе.
    """
    # Информация о сервисе онлайн-оплаты
    payment_service = cache_factory('payment_service', event['payment_service_id'])
    # Экземпляр класса сервиса онлайн-оплаты
    ps = payment_service['instance']

    # Получение общей суммы заказа в зависимости от возможных наценок/скидок

    # Процент сервисного сбора для конкретного типа заказа
    extra = event['settings']['extra'][order['type']]
    order['overall'] = ps.total_plus_extra(order['tickets'], order['total'], extra)

    # При доставке курьером
    if order['delivery'] == 'courier':
        # Общая сумма заказа (с учётом сервисного сбора и стоимости доставки курьером)
        order['overall'] = ps.total_plus_courier_price(order['overall'], order['courier_price'])

    # При онлайн-оплате
    if order['payment'] == 'online':
        # Общая сумма заказа (с учётом сервисного сбора и комиссии сервиса онлайн-оплаты)
        order['overall'] = ps.total_plus_commission(order['overall'])
