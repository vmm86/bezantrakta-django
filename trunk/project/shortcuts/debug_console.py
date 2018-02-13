from django.conf import settings


def debug_console(*args):
    """Вывод отладочной информации в консоль ТОЛЬКО при наличии булева параметра в настройках."""
    if settings.DEBUG and settings.BEZANTRAKTA_DEBUG_CONSOLE:
        print('\033[1;93m', sep='', end='')
        for i in range(len(args)):
            print(args[i], sep='', end=' ')
        print('\033[0;0m\n')

# if level == 'INFO':
#     self.stdout.write(self.style.WARNING(msg))
# elif level == 'SUCCESS':
#     self.stdout.write(self.style.SUCCESS(msg))
# elif level == 'NOTICE':
#     self.stdout.write(self.style.NOTICE(msg))
# elif level == 'ERROR':
#     self.stdout.write(self.style.ERROR(msg))
