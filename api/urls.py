from django.conf.urls import url

# События
from api.views.event import seats_and_prices
# Заказы
from api.views.order import prev_order_delete, initialize, reserve, change_type, processing
# Оплата
from api.views.payment import payment_handler, sngb_proxy

app_name = 'api'

event_urls = [
    # Периодическое получение списка доступных для продажи мест и списка цен в событии
    url(
        r'^event/seats_and_prices/$',
        seats_and_prices,
        name='event__seats_and_prices'
    ),
]

order_urls = [
    # Попытка удалить предыдущий предварительный резерв из другого события, если он был сделан ранее
    url(
        r'^order/prev_order_delete/$',
        prev_order_delete,
        name='order__prev_order_delete'
    ),
    # Получение информации о текущем предварительном резерве или создание нового пустого предварительного резерва
    url(
        r'^order/initialize/$',
        initialize,
        name='order__initialize'
    ),
    # Добавление/удаление билета в предварительном резерве
    # В зависимости от сервиса продажи билетов может работать или НЕ работать
    # В последнем случае всегда возвращается успешный результат со всеми переданными аргументами
    url(
        r'^order/reserve/$',
        reserve,
        name='order__reserve'
    ),
    # Изменение типа заказа на шаге 2 заказа билетов (ДО создания заказа)
    url(
        r'^order/change_type/$',
        change_type,
        name='order__change_type'
    ),
    # Обработка заказа после отправки формы на шаге 2 заказа билетов
    # Завершение заказа для оплаты наличными либо редирект на запрошенную форму для онлайн-оплаты
    url(
        r'^order/processing/$',
        processing,
        name='order__processing'
    ),
]

payment_urls = [
    # Проверка и обработка успешной оплаты
    url(
        r'^payment/success/$',
        payment_handler,
        name='payment__success'
    ),
    # Проверка и обработка НЕуспешной оплаты
    url(
        r'^payment/error/$',
        payment_handler,
        name='payment__error'
    ),

    # Предобработка успешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^payment/sngb_init/$',
        sngb_proxy,
        name='payment__sngb_init'
    ),
    # Предобработка НЕуспешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^payment/sngb_error/$',
        sngb_proxy,
        name='payment__sngb_error'
    ),
]

urlpatterns = event_urls + order_urls + payment_urls
