""" `bezantrakta` project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from project.views import error

urlpatterns = [
    # Сообщения об ошибках
    url(r'^error(?:/(?P<http_code>\d+))?/$', error, name='error'),

    url(r'^simsim/help/', include('docs.urls')),
    url(r'^simsim/', admin.site.urls),

    url(r'^api/', include('api.urls')),

    url(r'', include('bezantrakta.event.urls')),
    url(r'', include('bezantrakta.order.urls')),
    url(r'', include('bezantrakta.seo.urls')),
    url(r'', include('bezantrakta.article.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
