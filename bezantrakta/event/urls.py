from django.conf.urls import url

# from .views import EventVenueAutocomplete

from .views import events_on_index
from .views import event
from .views import category
from .views import search

app_name = 'event'

urlpatterns = [
    # url(
    #     r'^simsim/venue-autocomplete/$',
    #     EventVenueAutocomplete.as_view(),
    #     name='venue_autocomplete',
    # ),
    url(
        r'^$',
        events_on_index,
        name='events_on_index'
    ),
    url(
        r'^afisha/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)-(?P<minute>\d+)/(?P<slug>[\w-]+)/$',
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
    ),
]
