from django.conf import settings


def environment(request):
    """
    Получение параметров рабочего окружения и их добавление в template context.
    """
    return {
        'ENVIRONMENT_NAME': settings.ENVIRONMENT['NAME'],
        'ENVIRONMENT_COLOR': settings.ENVIRONMENT['COLOR'],
    }
