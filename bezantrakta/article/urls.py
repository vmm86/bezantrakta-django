from django.conf.urls import url

from . import views

app_name = 'article'

urlpatterns = [
    url(r'^$', views.show_index, name='show_index'),
    url(r'^(?P<slug>[\w-]+)/$', views.show_article, name='show_article'),
]
