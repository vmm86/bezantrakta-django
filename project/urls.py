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

from project.views import error, error_400, error_403, error_404, error_410, error_500, error_503

urlpatterns = [
    # Сообщения об ошибках
    url(r'^error/', error, name='error'),
    url(r'^error_400/', error_400, name='error_400'),
    url(r'^error_403/', error_403, name='error_403'),
    url(r'^error_404/', error_404, name='error_404'),
    url(r'^error_410/', error_410, name='error_410'),
    url(r'^error_500/', error_500, name='error_500'),
    url(r'^error_503/', error_503, name='error_503'),

    url(r'^simsim/', admin.site.urls),
    # url(r'^simsim/doc/', include('django.contrib.admindocs.urls')),

    url(r'', include('third_party.ticket_service.urls')),
    url(r'', include('third_party.payment_service.urls')),

    url(r'', include('bezantrakta.event.urls')),
    url(r'', include('bezantrakta.seo.urls')),
    url(r'', include('bezantrakta.order.urls')),
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
