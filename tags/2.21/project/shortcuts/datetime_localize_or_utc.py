def datetime_localize_or_utc(dt, tz):
    """Локализация даты/времени или приведение к UTC.

    * Если в дате/времени указан часовой пояс - дате/время остаётся неизменной (должно писаться в БД в UTC!).
    * Если в дате/времени НЕ указан часовой пояс - дате/время локализуется с учётом часового пояса.

    Args:
        dt (datetime.datetime): Дата/время.
        tz (pytz.tzfile): Часовой пояс ``pytz``.

    Returns:
        datetime.datetime: Преобразованная дата/время.
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = tz.localize(dt)

    return dt
