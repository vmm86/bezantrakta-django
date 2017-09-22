from collections import namedtuple

from django.contrib import messages


# Фабрика для помещения сообщений в очередь вывода
message = namedtuple('Message', 'level text')
message.__new__.__defaults__ = (None,) * len(message._fields)


def render_messages(request, msgs):
    """Добавление в очередь на вывод в шаблоне одного или более статусных сообщений.

    Сообщения кладутся в очередь ``messages`` и выводятся шаблоне того вида, в котором вызывается эта функция.

    Args:
        msgs (dict): Сообщения для вывода. Ключи ``msgs`` - уровень уведомления (``debug``, ``info``, ``success``, ``warning``, ``error``). Значения ``msgs`` - текстовые сообщения для вывода.
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
