from django.conf import settings


def environment(request):
    """Получение параметров текущего рабочего окружения и их добавление в контекст шаблона."""
    return {
        'ENVIRONMENT_NAME':  settings.ENVIRONMENT['NAME'],
        'ENVIRONMENT_COLOR': settings.ENVIRONMENT['COLOR'],
    }
