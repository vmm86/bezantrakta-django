from django.conf.urls import url

# Сервисы продажи билетов
from api.views.third_party.ticket_service import seats_and_prices, reserve
# Сервисы онлайн-оплаты
from api.views.third_party.payment_service import payment_handler, sngb_proxy

app_name = 'api'

ticket_service_urls = [
    # Периодическое получение списка доступных для продажи мест и списка цен в событии
    url(
        r'^ts/seats_and_prices/$',
        seats_and_prices,
        name='seats_and_prices'
    ),

    # Предварительный резерв места (добавление в резерв или удаление из резерва)
    # В зависимости от сервиса продажи билетов может работать или НЕ работать
    # В последнем случае всегда возвращается успешный результат со всеми переданными аргументы места
    url(
        r'^ts/reserve/$',
        reserve,
        name='reserve'
    ),
]

payment_service_urls = [
    # Проверка и обработка успешной оплаты
    url(
        r'^ps/success/$',
        payment_handler,
        name='payment_success'
    ),
    # Проверка и обработка НЕуспешной оплаты
    url(
        r'^ps/error/$',
        payment_handler,
        name='payment_error'
    ),

    # Предобработка успешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^ps/sngb_init/$',
        sngb_proxy,
        name='sngb_init'
    ),
    # Предобработка НЕуспешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^ps/sngb_error/$',
        sngb_proxy,
        name='sngb_error'
    ),
]

urlpatterns = ticket_service_urls + payment_service_urls
