from django.conf.urls import url

from .views.events_on_index import events_on_index
from .views.event import event
from .views.category import category
from .views.search import search

app_name = 'event'

urlpatterns = [
    url(
        r'^$',
        events_on_index,
        name='events_on_index'
    ),
    url(
        r'^afisha/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[\w-]+)/$',
        event,
        name='event'
    ),
    url(
        r'^afisha/category/(?P<slug>[\w-]+)/$',
        category,
        name='category'
    ),
    url(
        r'^search/$',
        search,
        name='search'
    )
]
