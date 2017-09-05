import datetime
import uuid
from collections import namedtuple
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.utils import timezone


def timezone_now():
    """Получение текущей даты и времени в текущем часовом поясе.

    Returns:
        datetime: Текущая дата и время.
    """
    return timezone.now()


def base_template_context_processor(request):
    """Запускать context_processor для отображения в базовом шаблоне только в базовом шаблоне.
    Т.е. на всех страницах, кроме процесса заказа билетов.

    Returns:
        bool: Запускать context_processor или нет.
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


def render_messages(request, msgs):
    """Добавление в очередь одного или более сообщений сообщений.

    msgs - словарь с сообщениями для вывода.
    Его ключи - уровень уведомления ('debug', 'info', 'success', 'warning', 'error').
    Его значения - текстовые сообщения для вывода.

    Сообщения кладутся в очередь messages и выводятся шаблоне того вида, в котором вызывается эта функция.

    Args:
        msgs (dict): Сообщения для вывода.
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


def decimal_price(value):
    """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа Decimal.

    Args:
        value (str): Входное значение (в любом случае строка - для обхода проблем с округлением float).

    Returns:
        Decimal: Денежная сумма.
    """
    return Decimal(str(value)).quantize(Decimal('1.00'))


def datetime_localize_or_utc(dt, tz):
    """
    Если в дате/времени указан часовой пояс - дате/время остаётся неизменным (должно писаться в БД в UTC!).
    Если в дате/времени НЕ указан часовой пояс - дате/время локализуется с учётом часового пояса.

    Args:
        dt (datetime): Дата и время
        tz (pytz.tzfile): Часовой пояс pytz

    Returns:
        datetime: Дата/время
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = tz.localize(dt)

    return dt


def json_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        obj = obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        obj = str(obj)
    else:
        obj = None

    return obj
