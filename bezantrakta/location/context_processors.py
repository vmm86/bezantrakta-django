from django.conf import settings


def environment(request):
    return {
        'ENVIRONMENT_NAME': settings.ENVIRONMENT['NAME'],
        'ENVIRONMENT_COLOR': settings.ENVIRONMENT['COLOR'],
    }
