from django.conf.urls import url

from .views import (
    events_on_index,
    event,
    calendar, category, venue, search
)

app_name = 'event'

urlpatterns = [
    # Показ событий на главной странице
    url(
        r'^$',
        events_on_index,
        name='events_on_index'
    ),
    # Шаг 1 заказа билетов (выбор билетов на схеме зала)
    url(
        r'^afisha/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)-(?P<minute>\d+)/(?P<slug>[\w-]+)/$',
        event,
        name='event'
    ),
    # Фильтр событий по дате в календаре
    url(
        r'^afisha/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$',
        calendar,
        name='calendar'
    ),
    # Фильтр событий по категории
    url(
        r'^afisha/category/(?P<slug>[\w-]+)/$',
        category,
        name='category'
    ),
    # Фильтр событий по залу (месту проведения событий)
    url(
        r'^afisha/venue/(?P<slug>[\w-]+)/$',
        venue,
        name='venue'
    ),
    # Фильтр событий по тексту (поиск событий)
    url(
        r'^afisha/search/$',
        search,
        name='search'
    ),
]
