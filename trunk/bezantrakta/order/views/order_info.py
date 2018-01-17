from project.cache import cache_factory

from bezantrakta.order.settings import ORDER_TYPE


def order_info(request, event, customer, order):
    """Заготовка для работы с заказаом на сервере при получении AJAX-запроса от клиента.

    Args:
        event (TYPE): Информация о событии.
        order (TYPE): Информация о заказе.
    """
    # Информация о сервисе онлайн-оплаты
    payment_service = cache_factory('payment_service', event['payment_service_id'])
    # Экземпляр класса сервиса онлайн-оплаты
    ps = payment_service['instance']

    # Процент сервисного сбора для конкретного типа заказа
    extra = event['settings']['extra'][order['type']]

    # Получение общей суммы заказа в зависимости от возможных наценок/скидок

    # Для любого типа заказа - с учётом сервисного сбора для каждого билета в заказе (если он задан)
    order['overall'] = ps.total_plus_extra(order['tickets'], order['total'], extra)

    # При доставке курьером - с учётом стоимости доставки курьером (если она задана)
    if customer['delivery'] == 'courier':
        # Общая сумма заказа (с учётом сервисного сбора и стоимости доставки курьером)
        order['overall'] = ps.total_plus_courier_price(order['overall'], order['courier_price'])

    # При онлайн-оплате - с учётом комиссии сервиса онлайн-оплаты (если она задана)
    if customer['payment'] == 'online':
        # Общая сумма заказа (с учётом сервисного сбора и комиссии сервиса онлайн-оплаты)
        order['overall'] = ps.total_plus_commission(order['overall'])
