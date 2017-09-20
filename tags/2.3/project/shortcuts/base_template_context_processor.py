from django.conf import settings


def base_template_context_processor(request):
    """Запускать процессор контекста для отображения ТОЛЬКО в базовом шаблоне (везде, кроме процесса заказа билетов).

    Returns:
        bool: Запускать процессор контекста или нет.
    """
    # Если сайт опубликован
    domain_is_published = request.domain_is_published

    # Если пользователь НЕ в админ-панели
    frontend = settings.BEZANTRAKTA_ADMIN_URL not in request.url_path

    # Если текущий вид НЕ принадлежит процессу оформления заказа билетов
    order_progress = (
        True if
        request.resolver_match is not None and request.resolver_match.url_name in settings.BEZANTRAKTA_ORDER_VIEWS else
        False
    )

    return True if (domain_is_published and frontend and not order_progress) else False
