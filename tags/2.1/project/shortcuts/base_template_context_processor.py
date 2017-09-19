from collections import namedtuple

from django.conf import settings


def base_template_context_processor(request):
    """Запускать процессор контекста для отображения ТОЛЬКО в базовом шаблоне.
    Т.е. на всех страницах, кроме процесса заказа билетов.

    Returns:
        bool: Запускать процессор контекста или нет.
    """
    # Если сайт опубликован
    domain_is_published = request.domain_is_published
    # print('domain_is_published:', domain_is_published)

    # Если пользователь не в админ-панели
    frontend = settings.BEZANTRAKTA_ADMIN_URL not in request.url_path
    # print('frontend:', frontend)

    # Если текущий вид не принадлежит к процессу оформления заказа билетов
    order_in_progress = False
    for v in settings.BEZANTRAKTA_ORDER_VIEWS:
        if request.resolver_match.url_name == v:
            order_in_progress = True

    # print('order_in_progress:', order_in_progress)

    return True if domain_is_published and frontend and not order_in_progress else False


# Фабрика для помещения сообщений в очередь вывода
message = namedtuple('Message', 'level text')
message.__new__.__defaults__ = (None,) * len(message._fields)
