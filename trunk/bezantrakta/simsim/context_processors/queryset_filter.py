from django.conf import settings


def queryset_filter(request):
    """
    Получение параметров города/сайта,
    выбранного для фильтрации данных в админ-панели,
    и их добавление в template context.
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
