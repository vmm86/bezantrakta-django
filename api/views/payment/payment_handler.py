import uuid

from django.shortcuts import redirect

from project.shortcuts import BOOLEAN_VALUES, message, render_messages, timezone_now

from api.views.payment.success_or_error import success_or_error

from bezantrakta.order.order_basket import OrderBasket


def payment_handler(request):
    """Проверка и обработка заказа с онлайн-оплатой после возвращения с платёжной формы."""
    # Получение уникальных идентификаторов события и заказа из GET-парамеров
    event_uuid = request.GET.get('event_uuid', None)
    try:
        event_uuid = uuid.UUID(event_uuid)
    except (TypeError, ValueError):
        event_uuid = None

    order_uuid = request.GET.get('order_uuid', None)
    try:
        order_uuid = uuid.UUID(order_uuid)
    except (TypeError, ValueError):
        order_uuid = None

    # Сообщение об ошибке при НЕполучении необходимых для обработки данных
    if not event_uuid or not order_uuid:
        msgs = [
            message('error', 'К сожалению, произошла ошибка - такого заказа не существует. 🙁'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')

    # Попытка получить статус оплаты сразу из GET-парамеров
    # (возможный обходной вариант для сервисов, у которых нельзя запросить статус оплаты отдельным запросом)
    success = request.GET.get('success', None)
    payment_id = request.GET.get('payment_id', None)
    error_code = request.GET.get('code', None)
    error_message = request.GET.get('message', None)

    if success is not None:
        success = True if success in BOOLEAN_VALUES else False

    # Получение параметров предварительного резерва
    basket = OrderBasket(order_uuid=order_uuid, logger='bezantrakta.order')
    if not basket or not basket.order:
        # Сообщение об ошибке
        msgs = [
            message('error', 'Предварительный резерв некорректен или отсутствует. 🙁'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error')

    # Логирование обработки заказа
    basket.logger.info('\n----------Обработка оплаты заказа {}----------'.format(order_uuid))
    basket.logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(timezone_now()))

    basket.log()

    basket.logger.info('\nbasket.order payment start: {}'.format(basket.order))

    # Если статус оплаты не получен сразу и его требуется запросить отдельно
    if not success:
        # Проверка статуса оплаты
        payment_status = basket.payment_status()
    # Если статус оплаты приходит сразу в GET-парамерах
    else:
        payment_status = {
            'success':    success,
            'payment_id': payment_id,
            'code':       error_code,
            'message':    error_message,
        }

        # Сообщение об ошибке при НЕполучении идентификатора оплаты
        if payment_status['payment_id'] is None:
            msgs = [
                message('error', 'К сожалению, произошла ошибка - такая оплата не проводилась. 🙁'),
                message('info', '👉 <a href="{event_url}">Попробуйте заказать билеты ещё раз</a>.'.format(
                        event_url=basket.event_url)
                        ),
            ]
            render_messages(request, msgs)
            return redirect('error')

    # Обработка успешной или НЕуспешной оплаты
    result = success_or_error(basket, payment_status)

    # Если оплата завершилась успешно - редирект на шаг 3 с информацией о заказе
    if result['success']:
        return redirect('order:order_step_3', order_uuid=basket.order['order_uuid'])
    # Если оплата завершилась НЕуспешно - редирект на страницу с информацией об ошибке
    else:
        # Сборка очереди сообщений для вывода на странице ошибки
        msgs = []
        for item in result['messages']:
            msgs.append(message(item['level'], item['message']))

        render_messages(request, msgs)

        return redirect('error')
