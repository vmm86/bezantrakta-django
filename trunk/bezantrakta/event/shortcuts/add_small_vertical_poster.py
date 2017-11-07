from .process_event_data import process_event_data


def add_small_vertical_poster(query):
    """Добавление к результату запроса URL афиши `small_vertical` или заглушки по умолчанию.

    Метод выполняется как при фильтрации событий по какому-либо основанию (события на главной, в категории, из поиска),
    так и при выводе страницы конкретного события.

    Если обрабатывается множество событий - они перебираются в цикле.
    Если обрабатывается одно событие в словаре - перебираются его ключи.
    """
    if type(query) is not dict:
        for item in query:
            process_event_data(item)
    else:
        process_event_data(query)
