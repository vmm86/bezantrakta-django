import os.path

from django.conf import settings
from django.utils import timezone


# Получение сегодняшней даты в активном на данный момент часовом поясе.
today = timezone.now()


def add_small_vertical_poster(request, query):
    """
    Добавление к результату запроса URL афиши `small_vertical` или заглушки.
    Метод выполняется как при фильтрации событий по какому-либо основанию
    (события на главной, в категории, из поиска),
    так и при выводе страницы конкретного события.
    """
    def process_event_data(request, data):
        params = {}
        # Событие или группа
        if ('is_group' in data and data['is_group']) or ('is_in_group' in data and data['is_in_group']):
            params['item'] = 'group'
            params['datetime'] = data['group_datetime']
            params['slug'] = data['group_slug']
        else:
            params['item'] = 'event'
            params['datetime'] = data['event_datetime']
            params['slug'] = data['event_slug']
        # Дата и время события или группы в часовом поясе его города
        current_timezone = request.city_timezone
        try:
            params['datetime_localized'] = params['datetime'].astimezone(current_timezone)
        except AttributeError:
            pass
        else:

            poster_file = os.path.join(
                request.domain_slug,
                params['item'],
                ''.join(
                    (
                        params['datetime_localized'].strftime('%Y-%m-%d'),
                        '_',
                        params['datetime_localized'].strftime('%H-%M'),
                        '_',
                        params['slug'],
                    )
                ),
                'small_vertical.png',
            )
            # data['poster'] = ''.join(
            #     (settings.MEDIA_URL, poster_file)
            # )
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
            process_event_data(request, item)
    # Если обрабатывается одно событие в словаре - перебираются его ключи
    else:
        process_event_data(request, query)
