from django.conf import settings


def hide_test_events_in_production(event):
    """В production-версии сайта НЕ показываются афиши тестовых событий.

    Страницы тестовых событий в production можно открывать напрямую из админ-панели, нажимая на кнопку "*Смотреть на сайте*".

    Args:
        event (dict): Информация о событии.

    Returns:
        bool: Показывать конкретное событие или нет.
    """
    # В development-версии сайта показываются афиши всех актуальных событий
    if settings.DEBUG:
        return True
    # В production-версии сайта показываются афиши всех актуальных событий, кроме тестовых
    else:
        if 'test' not in event['settings'] or not event['settings']['test']:
            return True
        else:
            return False
