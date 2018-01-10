from django.utils import timezone


def timezone_now():
    """Получение текущей даты/времени в текущем часовом поясе.

    Returns:
        datetime.datetime: Текущая дата/время.
    """
    return timezone.now()
