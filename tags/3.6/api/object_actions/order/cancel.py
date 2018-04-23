from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket


def cancel(order_uuid):
    """Отмена заказа с оффлайн-оплатой.

    Args:
        order_uuid (uuid.UUID): Уникальный идентификатор заказа.

    Returns:
        dict: Информация о результате отмены.
    """
    # Получение экземпляра заказа
    basket = OrderBasket(order_uuid=order_uuid, logger='bezantrakta.cancel')

    if not basket or not basket.order:
        response = {'success': False, 'message': 'Отсутствует заказ с указанным UUID'}
        return response

    basket.logger.info('\n----------Отмена заказа {}----------'.format(basket.order['order_uuid']))
    basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

    basket.log()

    cancel = basket.order_cancel()

    basket.delete()

    return cancel
