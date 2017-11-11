from django.conf import settings

from bezantrakta.location.models import City, Domain


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

        # try:
        #     current_city = City.objects.get(slug=city_slug)
        # except City.DoesNotExist:
        #     city_id = 0
        # else:
        #     city_id = current_city.id

        try:
            current_domain = Domain.objects.get(slug=domain_slug)
        except Domain.DoesNotExist:
            domain_id = 0
        else:
            domain_id = current_domain.id

        return {
            # 'bezantrakta_admin_city_id': city_id,
            'bezantrakta_admin_city_slug': city_slug,
            'bezantrakta_admin_domain_slug': domain_slug,
            'bezantrakta_admin_domain_id': domain_id,
        }
    else:
        return {}
