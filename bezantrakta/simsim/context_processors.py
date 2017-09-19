from bezantrakta.location.models import Domain


def domain_filter(request):
    """
    Получение параметров выбранного для фильтрации сайта и их добавление в template context.
    """
    domain_slug = request.COOKIES.get('bezantrakta_domain', None)

    try:
        current_domain = Domain.objects.get(slug=domain_slug)
    except Domain.DoesNotExist:
        domain_id = 0
    else:
        domain_id = current_domain.id

    return {
        'bezantrakta_domain_slug': domain_slug,
        'bezantrakta_domain_id': domain_id,
    }
