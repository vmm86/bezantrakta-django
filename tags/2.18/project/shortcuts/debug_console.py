from django.conf import settings


def debug_console(*args):
    """Вывод отладочной информации в консоль ТОЛЬКО в development-окружении.

    Args:
        *args: Description
    """
    if settings.DEBUG:
        for i in range(len(args)):
            print('\033[1;93m', args[i], '\033[0;0m', sep='', end=' ')
    print('\n')
