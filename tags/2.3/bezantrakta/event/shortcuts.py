import os

from django.conf import settings


def add_small_vertical_poster(request, query):
    """
    Добавление к результату запроса URL афиши `small_vertical` или заглушки.
    Метод выполняется как при фильтрации событий по какому-либо основанию
    (события на главной, в категории, из поиска),
    так и при выводе страницы конкретного события.

    Если обрабатывается множество событий - они перебираются в цикле.
    Если обрабатывается одно событие в словаре - перебираются его ключи.
    """
    if type(query) is not dict:
        for item in query:
            process_event_data(request, item)
    else:
        process_event_data(request, query)


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
    datetime_localized = params['datetime'].astimezone(current_timezone)

    poster_file = os.path.join(
        request.domain_slug,
        params['item'],
        '{date}_{time}_{slug}'.format(
            date=datetime_localized.strftime('%Y-%m-%d'),
            time=datetime_localized.strftime('%H-%M'),
            slug=params['slug']
        ),
        'small_vertical.png',
    )
    if os.path.isfile(os.path.join(settings.MEDIA_ROOT, poster_file)):
        data['poster'] = '{media_url}{poster_file}'.format(
            media_url=settings.MEDIA_URL,
            poster_file=poster_file
        )
        data['poster_path'] = '{media_root}/{poster_file}'.format(
            media_root=settings.MEDIA_ROOT,
            poster_file=poster_file
        )
    else:
        data['poster'] = '{media_url}global/event/small_vertical.png'.format(
            media_url=settings.MEDIA_URL
        )
        data['poster_path'] = '{media_root}/global/event/small_vertical.png'.format(
            media_root=settings.MEDIA_ROOT
        )
