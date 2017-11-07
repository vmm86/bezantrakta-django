import os
import pytz

from django.conf import settings


def process_event_data(data):
    params = {}
    # Событие или группа
    if ('is_group' in data and data['is_group']) or ('is_in_group' in data and data['is_in_group']):
        params['item'] = 'group'
        params['uuid'] = data['group_uuid']
    else:
        params['item'] = 'event'
        params['uuid'] = data['event_uuid']
    # Дата и время события или группы в часовом поясе города
    city_timezone = pytz.timezone(data['city_timezone'])
    datetime_localized = data['event_datetime'].astimezone(city_timezone)

    poster_path = os.path.join(
        data['domain_slug'],
        params['item'],
        str(params['uuid'])
    )

    # ВРЕМЕННО до перехода на сохранение афиш по UUID
    poster_path_old = os.path.join(
        data['domain_slug'],
        params['item'],
        '{date}_{time}_{slug}'.format(
            date=datetime_localized.strftime('%Y-%m-%d'),
            time=datetime_localized.strftime('%H-%M'),
            slug=data['event_slug']
        )
    )
    # ВРЕМЕННО до перехода на сохранение афиш по UUID

    poster_file_extensions = ('png', 'jpg', 'jpeg', 'gif', )

    for ext in poster_file_extensions:
        poster_file = 'small_vertical.{ext}'.format(ext=ext)
        print('path: ', '\n', os.path.join(settings.MEDIA_ROOT, poster_path, poster_file))
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, poster_path, poster_file)):
            data['poster'] = '{media_url}{poster_path}/{poster_file}'.format(
                media_url=settings.MEDIA_URL,
                poster_path=poster_path,
                poster_file=poster_file
            )
            data['poster_path'] = '{media_root}/{poster_path}/{poster_file}'.format(
                media_root=settings.MEDIA_ROOT,
                poster_path=poster_path,
                poster_file=poster_file
            )
            print('found UUID poster: ', '\n', data['poster'], '\n', data['poster_path'])
            break
        # ВРЕМЕННО до перехода на сохранение афиш по UUID
        elif os.path.isfile(os.path.join(settings.MEDIA_ROOT, poster_path_old)):
            data['poster'] = '{media_url}{poster_path}/{poster_file}'.format(
                media_url=settings.MEDIA_URL,
                poster_path=poster_path_old,
                poster_file=poster_file
            )
            data['poster_path'] = '{media_root}/{poster_path}/{poster_file}'.format(
                media_root=settings.MEDIA_ROOT,
                poster_path=poster_path_old,
                poster_file=poster_file
            )
            print('found old poster: ', '\n', data['poster'], '\n', data['poster_path'])
            break
        # ВРЕМЕННО до перехода на сохранение афиш по UUID
    else:
        data['poster'] = '{media_url}global/event/small_vertical.png'.format(
            media_url=settings.MEDIA_URL
        )
        data['poster_path'] = '{media_root}/global/event/small_vertical.png'.format(
            media_root=settings.MEDIA_ROOT
        )
