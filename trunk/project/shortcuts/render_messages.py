from collections import namedtuple

from django.contrib import messages


# Фабрика для помещения сообщений в очередь вывода
message = namedtuple('Message', 'level text')
message.__new__.__defaults__ = (None,) * len(message._fields)


def render_messages(request, msgs):
    """Добавление статусных сообщений в очередь ``messages`` и их последующий вывод в шаблоне того или иного вида.

    Args:
        msgs (dict): Сообщения для вывода.

            Ключи ``msgs`` - уровни уведомления:
                * ``debug``
                * ``info``
                * ``success``
                * ``warning``
                * ``error``

            Значения ``msgs`` - текстовые сообщения для вывода.
    """
    for msg in msgs:
        if msg.level == 'debug':
            messages.debug(request, msg.text)
        elif msg.level == 'info':
            messages.info(request, msg.text)
        elif msg.level == 'success':
            messages.success(request, msg.text)
        elif msg.level == 'warning':
            messages.warning(request, msg.text)
        elif msg.level == 'error':
            messages.error(request, msg.text)
