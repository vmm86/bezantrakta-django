from django.conf.urls import url
from django.views.generic import RedirectView

from .views import browserconfig, manifest, robots_txt, yandex_manifest

app_name = 'seo'

urlpatterns = [
    url(r'^browserconfig\.xml$', browserconfig, name='browserconfig'),
    url(r'^manifest\.json$', manifest, name='manifest'),
    url(r'^robots\.txt$', robots_txt, name='robots_txt'),
    url(r'^yandex\.manifest\.json$', yandex_manifest, name='yandex_manifest'),

    # Редиректы для возможных запросов к иконкам в корне сайта
    url(
        r'^favicon\.ico$',
        RedirectView.as_view(url='/static/global/ico/favicon.ico', permanent=True),
        name='favicon'
    ),
    url(
        r'^android-chrome-32x32\.png$',
        RedirectView.as_view(url='/static/global/ico/android-chrome-32x32.png', permanent=True),
        name='android_chrome_32'
    ),
    url(
        r'^android-chrome-36x36\.png$',
        RedirectView.as_view(url='/static/global/ico/android-chrome-36x36.png', permanent=True),
        name='android_chrome_36'
    ),
    url(
        r'^android-chrome-48x48\.png$',
        RedirectView.as_view(url='/static/global/ico/android-chrome-48x48.png', permanent=True),
        name='android_chrome_48'
    ),
    url(
        r'^android-chrome-72x72\.png$',
        RedirectView.as_view(url='/static/global/ico/android-chrome-72x72.png', permanent=True),
        name='android_chrome_72'
    ),
    url(
        r'^android-chrome-96x96\.png$',
        RedirectView.as_view(url='/static/global/ico/android-chrome-96x96.png', permanent=True),
        name='android_chrome_96'
    ),
    url(
        r'^android-chrome-144x144\.png$',
        RedirectView.as_view(url='/static/global/ico/android-chrome-144x144.png', permanent=True),
        name='android_chrome_144'
    ),
    url(
        r'^android-chrome-192x192\.png$',
        RedirectView.as_view(url='/static/global/ico/android-chrome-192x192.png', permanent=True),
        name='android_chrome_192'
    ),
    url(
        r'^apple-touch-icon\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon.png', permanent=True),
        name='apple_touch_icon'
    ),
    url(
        r'^apple-touch-icon-57x57\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-57x57.png', permanent=True),
        name='apple_touch_icon_57'
    ),
    url(
        r'^apple-touch-icon-60x60\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-60x60.png', permanent=True),
        name='apple_touch_icon_60'
    ),
    url(
        r'^apple-touch-icon-72x72\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-72x72.png', permanent=True),
        name='apple_touch_icon_72'
    ),
    url(
        r'^apple-touch-icon-76x76\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-76x76.png', permanent=True),
        name='apple_touch_icon_76'
    ),
    url(
        r'^apple-touch-icon-114x114\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-114x114.png', permanent=True),
        name='apple_touch_icon_114'
    ),
    url(
        r'^apple-touch-icon-120x120\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-120x120.png', permanent=True),
        name='apple_touch_icon_120'
    ),
    url(
        r'^apple-touch-icon-144x144\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-144x144.png', permanent=True),
        name='apple_touch_icon_144'
    ),
    url(
        r'^apple-touch-icon-152x152\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-152x152.png', permanent=True),
        name='apple_touch_icon_152'
    ),
    url(
        r'^apple-touch-icon-180x180\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-180x180.png', permanent=True),
        name='apple_touch_icon_180'
    ),
    url(
        r'^apple-touch-icon-precomposed\.png$',
        RedirectView.as_view(url='/static/global/ico/apple-touch-icon-precomposed.png', permanent=True),
        name='apple_touch_icon_precomposed'
    ),
    url(
        r'^mstile-70x70\.png$',
        RedirectView.as_view(url='/static/global/ico/mstile-70x70.png', permanent=True),
        name='mstile_70'
    ),
    url(
        r'^mstile-144x144\.png$',
        RedirectView.as_view(url='/static/global/ico/mstile-144x144.png', permanent=True),
        name='mstile_144'
    ),
    url(
        r'^mstile-150x150\.png$',
        RedirectView.as_view(url='/static/global/ico/mstile-150x150.png', permanent=True),
        name='mstile_150'
    ),
    url(
        r'^mstile-310x310\.png$',
        RedirectView.as_view(url='/static/global/ico/mstile-310x310.png', permanent=True),
        name='mstile_310'
    ),
    url(
        r'^mstile-310x150\.png$',
        RedirectView.as_view(url='/static/global/ico/mstile-310x150.png', permanent=True),
        name='mstile_310_150'
    ),
    url(
        r'^yandex-tableau\.png$',
        RedirectView.as_view(url='/static/global/ico/yandex-tableau.png', permanent=True),
        name='yandex_tableau'
    ),
]
