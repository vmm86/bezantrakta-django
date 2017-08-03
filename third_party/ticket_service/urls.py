from django.conf.urls import url

from .views import discover, reserve, seats

app_name = 'ticket_service'

urlpatterns = [
    url(
        r'^ts/seats/$',
        seats,
        name='seats'
    ),
    url(
        r'^ts/reserve/$',
        reserve,
        name='reserve'
    ),
    url(
        r'^tasks/discover/$',
        discover,
        name='discover'
    ),
]
