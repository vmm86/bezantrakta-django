from project.shortcuts import timezone_now

from bezantrakta.order.order_basket import OrderBasket


def etickets_resend(order_uuid):
    """Отправить сообщение о заказе билетов повторно.

    Электронные билеты будут сгенерированы заново и вложены в сообщение.

    Args:
        order_uuid (uuid.UUID): Уникальный идентификатор заказа.

    Returns:
        dict: Информация о результате отправки.
    """
    # Получение экземпляра заказа
    basket = OrderBasket(order_uuid=order_uuid, logger='bezantrakta.order')

    if not basket or not basket.order:
        response = {'success': False, 'message': 'Отсутствует заказ с указанным UUID'}
        return response

    basket.logger.info('\n----------Повторная отправка билетов по заказу {}----------'.format(basket.order['order_uuid']))
    basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

    basket.log()

    # Отправка email администратору и покупателю
    # email_admin = basket.email_admin()
    email_customer = basket.email_customer()

    basket.delete()

    return email_customer
