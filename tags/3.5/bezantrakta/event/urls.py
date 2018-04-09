from django.conf.urls import url

from .views import (
    events_on_index,
    filter_calendar, filter_category, filter_venue, filter_search
)

app_name = 'event'

urlpatterns = [
    # Показ событий на главной странице
    url(
        r'^$',
        events_on_index,
        name='events_on_index'
    ),

    # Фильтр событий по дате в календаре
    url(
        r'^afisha/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$',
        filter_calendar,
        name='filter_calendar'
    ),
    # Фильтр событий по категории
    url(
        r'^afisha/category/(?P<slug>[\w-]+)/$',
        filter_category,
        name='filter_category'
    ),
    # Фильтр событий по залу (месту проведения событий)
    url(
        r'^afisha/venue/(?P<slug>[\w-]+)/$',
        filter_venue,
        name='filter_venue'
    ),
    # Фильтр событий по тексту (поиск событий)
    url(
        r'^afisha/search/$',
        filter_search,
        name='filter_search'
    ),
]
