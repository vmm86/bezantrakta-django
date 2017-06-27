import os.path

from django.conf import settings


def add_small_vertical_poster(request, query):
    """
    Добавление к результату запроса URL афиши `small_vertical` или заглушки.
    Метод выполняется как при фильтрации событий по какому-либо основанию
    (события на главной, в категории, на день календаря, из поиска),
    так и при выводе страницы конкретного события.
    """
    def process(request, data):
        # Дата и время события в часовом поясе его города
        current_timezone = request.city_timezone
        event_datetime_localized = data['datetime'].astimezone(current_timezone)

        poster_file = os.path.join(
            request.domain_slug,
            'event',
            ''.join(
                (
                    event_datetime_localized.strftime('%Y-%m-%d'),
                    '_',
                    event_datetime_localized.strftime('%H-%M'),
                    '_',
                    data['slug'],
                )
            ),
            'small_vertical.png',
        )
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, poster_file)):
            data['poster'] = ''.join(
                (settings.MEDIA_URL, poster_file)
            )
        else:
            data['poster'] = ''.join(
                (settings.MEDIA_URL, 'global/event/small_vertical.png')
            )

    # Если обрабатывается множество событий - они перебираются в цикле
    if type(query) is not dict:
        for item in query:
            process(request, item)
    # Если обрабатывается одно событие в словаре - перебираются его ключи
    else:
        process(request, query)
