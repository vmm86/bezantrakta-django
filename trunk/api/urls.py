from django.conf.urls import url

# События
from api.views.event import seats_and_prices
# Заказы
from api.views.order import prev_order_delete, reserve
# Оплата
from api.views.payment import payment_handler, sngb_proxy

app_name = 'api'

event_urls = [
    # Периодическое получение списка доступных для продажи мест и списка цен в событии
    url(
        r'^event/seats_and_prices/$',
        seats_and_prices,
        name='seats_and_prices'
    ),
]

order_urls = [
    # Удаление предыдущего заказа в другом событии при заходе в новое событие
    url(
        r'^order/prev_order_delete/$',
        prev_order_delete,
        name='prev_order_delete'
    ),

    # Предварительный резерв места (добавление в резерв или удаление из резерва)
    # В зависимости от сервиса продажи билетов может работать или НЕ работать
    # В последнем случае всегда возвращается успешный результат со всеми переданными аргументы места
    url(
        r'^order/reserve/$',
        reserve,
        name='reserve'
    ),
]

payment_urls = [
    # Проверка и обработка успешной оплаты
    url(
        r'^payment/success/$',
        payment_handler,
        name='payment_success'
    ),
    # Проверка и обработка НЕуспешной оплаты
    url(
        r'^payment/error/$',
        payment_handler,
        name='payment_error'
    ),

    # Предобработка успешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^payment/sngb_init/$',
        sngb_proxy,
        name='sngb_init'
    ),
    # Предобработка НЕуспешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^payment/sngb_error/$',
        sngb_proxy,
        name='sngb_error'
    ),
]

urlpatterns = event_urls + order_urls + payment_urls
