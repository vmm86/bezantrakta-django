from project.cache import cache_factory

from bezantrakta.order import OrderBasket


def new_blank_order(event_uuid):
    """Создание нового пустого предварительного резерва в текущем событии.

    Args:
        event_uuid (uuid.UUID): UUID события.

    Returns:
        bezantrakta.order.order_basket.OrderBasket: Новый пустой предварительный резерв.
    """
    # Информация о событии
    event = cache_factory('event', event_uuid)
    event_id = event['ticket_service_event']

    # Информация о сервисе продажи билетов
    ticket_service = cache_factory('ticket_service', event['ticket_service_id'])

    # Создание нового пустого предварительного резерва
    return OrderBasket(
        order_uuid=None,
        ticket_service_id=ticket_service['id'],
        event_uuid=event_uuid,
        event_id=event_id,
    )
