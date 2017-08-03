import os.path
import simplejson as json

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from third_party.ticket_service.models import TicketService
from third_party.ticket_service.ticket_service_abc import ticket_service_factory


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


def datetime_localize_or_utc(dt, tz):
    """
    Если в дате/времени указан часовой пояс - дате/время остаётся неизменным.
    Если в дате/времени НЕ указан часовой пояс - дате/время локализуется с учётом часового пояса.

    Args:
        dt (datetime): Дата/время
        tz (pytz.tzfile): Часовой пояс pytz

    Returns:
        datetime: Дата/время
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = tz.localize(dt)

    return dt


def ticket_service_instance_cached(event_uuid, ticket_service_id):
    """
    Кэширование параметров для инстанцирования экземпляров классов сервисов продажи билетов для конкретных событий.
    Нет необходимости для этого каждый раз делать запрос к базе данных.
    К каждому ключу добавляется параметр `updated`,
    чтобы по истечении определённого времени его можно было удалить из кэша для экономии памяти.
    """
    event_ts_mapping = cache.get_or_set('event_ts_mapping', {})

    try:
        event_ts_mapping[event_uuid] is not None
    except (KeyError, TypeError):
        # Требуемый сервис продажи билетов
        ticket_service = TicketService.objects.values(
            'slug',
            'settings',
        ).get(
            is_active=True,
            id=ticket_service_id,
        )
        # Получение настроек из JSON
        ticket_service['settings'] = json.loads(ticket_service['settings'])

        event_ts_mapping[event_uuid] = {}
        event_ts_mapping[event_uuid]['slug'] = ticket_service['slug']
        event_ts_mapping[event_uuid]['init'] = ticket_service['settings']['init']
        event_ts_mapping[event_uuid]['updated'] = today
        cache.set('event_ts_mapping', event_ts_mapping)
    finally:
        print('\nevent_ts_mapping[', event_uuid, ']:\n', event_ts_mapping[event_uuid], '\n')

        # Экземпляр класса требуемого сервиса продажи билетов
        ts = ticket_service_factory(
            event_ts_mapping[event_uuid]['slug'],
            event_ts_mapping[event_uuid]['init'],
        )

        return ts
