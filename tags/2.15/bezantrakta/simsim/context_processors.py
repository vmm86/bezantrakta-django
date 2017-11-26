from django.conf import settings


def environment(request):
    """
    Получение параметров рабочего окружения и их добавление в template context.
    """
    return {
        'ENVIRONMENT_NAME': settings.ENVIRONMENT['NAME'],
        'ENVIRONMENT_COLOR': settings.ENVIRONMENT['COLOR'],
    }


def queryset_filter(request):
    """
    Получение параметров выбранного для фильтрации города и сайта и их добавление в template context.
    """
    if settings.BEZANTRAKTA_ADMIN_URL in request.url_path:
        city_slug = request.COOKIES.get('bezantrakta_admin_city', None)
        domain_slug = request.COOKIES.get('bezantrakta_admin_domain', None)

        return {
            'bezantrakta_admin_city_slug': city_slug,
            'bezantrakta_admin_domain_slug': domain_slug,
        }
    else:
        return {}
