from bezantrakta.order.order_basket import OrderBasket


def new_blank_order(event_uuid):
    """Создание нового пустого предварительного резерва в текущем событии.

    Args:
        event_uuid (uuid.UUID): UUID события.

    Returns:
        bezantrakta.order.order_basket.OrderBasket: Новый пустой предварительный резерв.
    """
    # Создание нового пустого предварительного резерва
    return OrderBasket(order_uuid=None, event_uuid=event_uuid)
