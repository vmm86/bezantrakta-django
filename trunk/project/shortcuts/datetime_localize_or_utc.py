def datetime_localize_or_utc(dt, tz):
    """Локализация даты/времени или приведение к UTC.

    Args:
        dt (datetime.datetime): Дата/время.
        tz (pytz.tzfile): Часовой пояс ``pytz``.

    Returns:
        datetime.datetime: Преобразованная дата/время.
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = tz.localize(dt)

    return dt
