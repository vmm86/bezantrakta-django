from django.conf.urls import url

from .views import browserconfig, manifest, robots_txt, yandex_manifest

app_name = 'seo'

urlpatterns = [
    url(r'^browserconfig\.xml$', browserconfig, name='browserconfig'),
    url(r'^manifest\.json$', manifest, name='manifest'),
    url(r'^robots\.txt$', robots_txt, name='robots_txt'),
    url(r'^yandex\.manifest\.json$', yandex_manifest, name='yandex_manifest'),
]
