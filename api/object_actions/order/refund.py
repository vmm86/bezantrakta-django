from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket


def refund(order_uuid, amount, reason=None):
    """Возврат стоимости заказа по запросу покупателя.

    Метод последовательно осуществляет:
        * возврат заказа в сервисе продажи билетов (СПБ);
        * возврат заказа в серисе онлайн оплаты (СОО).

    Args:
        order_uuid (uuid.UUID): Уникальный идентификатор заказа.
        amount (decimal.Decimal): Сумма возврата.
        reason (str): Причина возврата.

    Returns:
        dict: Информация о результате возврата.
    """
    # Получение экземпляра заказа
    basket = OrderBasket(order_uuid=order_uuid, logger='bezantrakta.refund')

    if not basket or not basket.order:
        response = {'success': False, 'message': 'Отсутствует заказ с указанным UUID'}
        return response

    basket.logger.info('\n----------Возврат по заказу {}----------'.format(basket.order['order_uuid']))
    basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

    basket.log()

    refund = basket.order_refund(amount, reason)

    basket.delete()

    return refund
