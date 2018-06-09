from django.contrib.messages import get_messages
from django.shortcuts import redirect, render


def error(request, http_code=400):
    """Вывод сообщений для пользователя, как правило, в случае ошибок на сайте.

    Args:
        http_status_code (int, optional): Код HTTP-статуса (``400``, ``403``, ``404``, ``410``, ``500``, ``503``).
    """
    context = {}

    return render(request, 'error.html', context, status=http_code) if get_messages(request) else redirect('/')
