from django.conf.urls import url

from .views import seats_and_prices, reserve

app_name = 'ticket_service'

urlpatterns = [
    # Периодическое получение списка доступных для продажи мест и списка цен в событии
    url(
        r'^api/ts/seats_and_prices/$',
        seats_and_prices,
        name='seats_and_prices'
    ),
    # Предварительный резерв места (добавление в резерв или удаление из резерва)
    # В зависимости от сервиса продажи билетов может работать или НЕ работать
    # В последнем случае просто возвращается успешный результат со всеми переданными аргументы места
    url(
        r'^api/ts/reserve/$',
        reserve,
        name='reserve'
    ),
]
