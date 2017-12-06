from django.conf.urls import url

from .views import payment_handler, sngb_proxy

app_name = 'payment_service'

urlpatterns = [
    # Проверка и обработка успешной оплаты
    url(
        r'^api/ps/success/$',
        payment_handler,
        name='payment_success'
    ),
    # Проверка и обработка НЕуспешной оплаты
    url(
        r'^api/ps/error/$',
        payment_handler,
        name='payment_error'
    ),

    # Предобработка успешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^api/ps/sngb_init/$',
        sngb_proxy,
        name='sngb_init'
    ),
    # Предобработка НЕуспешной оплаты в СНГБ (вынужденный костыль)
    url(
        r'^api/ps/sngb_error/$',
        sngb_proxy,
        name='sngb_error'
    ),
]
