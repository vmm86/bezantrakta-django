from django.conf.urls import url

from .views import payment_success, payment_error

app_name = 'payment_service'

urlpatterns = [
    # Оформление удачной оплаты
    url(
        r'^api/ps/success/$',
        payment_success,
        name='payment_success'
    ),
    # Оформление НЕудачной оплаты
    url(
        r'^api/ps/error/$',
        payment_error,
        name='payment_error'
    ),
]
