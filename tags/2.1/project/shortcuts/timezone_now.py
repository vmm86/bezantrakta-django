from django.utils import timezone


def timezone_now():
    """Получение текущей даты и времени в текущем часовом поясе.

    Returns:
        datetime.datetime: Текущая дата и время.
    """
    return timezone.now()
