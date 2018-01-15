import os
import simplejson as json
from dateutil.parser import parse

from django.conf import settings
from django.db.models import F
from django.urls.base import reverse

from project.cache import ProjectCache
from project.shortcuts import build_absolute_url, debug_console, humanize_date, timezone_now

from bezantrakta.event.models import Event, EventGroupBinder


class EventCache(ProjectCache):
    """Кэширование событий или групп в модели ``event.Event``.

    Attributes:
        entities (tuple): Перечень моделей или других сущностей для создания кэша.
        today (datetime.datetime): Текущая дата и время.
        substitutes (dict): Парамтеры для замены в группе или в событии.

            Содержимое ``substitutes``:
                * **group** (tuple): Параметры события для замены в родительской группе.
                * **event** (tuple): Параметры группы для замены в дочернем событии.

        override (bool): Заменять ли указанные параметры группы из события или события из группы при получении кэша.
    """
    entities = ('event', 'group',)
    today = timezone_now()
    substitutes = {
        'event_to_group': (
            # 'event_title',
            'event_slug',
            'event_datetime',
            'event_date',
            'event_time',
            'event_min_price',
            'event_venue_title',
            'url',
        ),
        'group_to_event': (
            'event_title',
            'event_description',
            'event_text',
            'event_min_age',
            'event_category_slug',
            'event_category_title',
        ),
    }
    override = True

    def set_cache_key(self, entity, object_id, **kwargs):
        super().set_cache_key(entity, object_id, **kwargs)

        self.override = False if 'override' in kwargs and not kwargs['override'] else True

    def get_model_object(self, object_id, **kwargs):
        return Event.objects.select_related(
                'event_venue',
                'domain'
            ).annotate(
                # Параметры события
                event_uuid=F('id'),
                event_title=F('title'),
                event_slug=F('slug'),
                event_datetime=F('datetime'),
                event_description=F('description'),
                event_keywords=F('keywords'),
                event_text=F('text'),
                event_min_price=F('min_price'),
                event_min_age=F('min_age'),
                event_category_slug=F('event_category__slug'),
                event_category_title=F('event_category__title'),
                event_venue_title=F('event_venue__title'),
                event_venue_city=F('event_venue__city__title'),
                event_promoter=F('promoter'),
                event_seller=F('seller'),
                # Параметры группы, если событие в неё входит
                group_uuid=F('event_groups'),

                payment_service_id=F('ticket_service__payment_service__id'),

                domain_slug=F('domain__slug'),

                city_timezone=F('domain__city__timezone'),
            ).values(
                'is_published',
                'is_on_index',
                'is_group',

                'event_uuid',
                'event_title',
                'event_slug',
                'event_datetime',
                'event_description',
                'event_keywords',
                'event_text',
                'event_min_price',
                'event_min_age',
                'event_category_slug',
                'event_category_title',
                'event_venue_title',
                'event_venue_city',
                'event_promoter',
                'event_seller',

                'group_uuid',

                'settings',

                'ticket_service_id',
                'ticket_service_event',
                'ticket_service_scheme',

                'payment_service_id',

                'domain_id',
                'domain_slug',

                'city_timezone'
            ).get(
                event_uuid=object_id,
            )

    def cache_preprocessing(self, **kwargs):
        # Человекопонятные локализованные дата и время события
        event_datetime_localized = self.value['event_datetime'].astimezone(self.value['city_timezone'])
        self.value['event_date'] = humanize_date(event_datetime_localized)
        self.value['event_time'] = event_datetime_localized.strftime('%H:%M')

        # Полный URL страницы события
        url = reverse(
            'event:event',
            args=[
                event_datetime_localized.strftime('%Y'),
                event_datetime_localized.strftime('%m'),
                event_datetime_localized.strftime('%d'),
                event_datetime_localized.strftime('%H'),
                event_datetime_localized.strftime('%M'),
                self.value['event_slug']
            ]
        )
        self.value['url'] = build_absolute_url(self.value['domain_slug'], url)

        # Содержится ли событие в группе - приведение к bool для удобства
        self.value['is_in_group'] = (
            True if
            not self.value['is_group'] and self.value['group_uuid'] is not None else
            False
        )

        # Приведение часового пояса города к str перед кэшированием во избежание исключения
        self.value['city_timezone'] = str(self.value['city_timezone'])

        if self.value['is_group']:
            # group_events = EventGroupBinder.objects.select_related(
            #     'event',
            #     'domain',
            # ).annotate(
            #     title=F('event__title'),
            #     slug=F('event__slug'),
            #     datetime=F('event__datetime'),
            #     venue=F('event__event_venue__title'),
            # ).filter(
            #     group=self.value['event_uuid'],
            #     event__is_published=True,
            #     event__datetime__gt=self.today,
            # ).values(
            #     'title',
            #     'slug',
            #     'datetime',
            #     'venue',
            #     'caption',
            # ).order_by(
            #     'datetime'
            # )

            # Получение списка актуальных событий на текущий момент
            events_in_group = EventGroupBinder.objects.filter(
                group_id=self.value['event_uuid'],
                event__datetime__gt=self.today,
            ).values_list('event__id', flat=True).order_by('event__datetime', 'event__ticket_service_event')
            self.value['events_in_group'] = (
                [event_uuid for event_uuid in events_in_group] if
                len(events_in_group) > 0 else
                None
            )

            # Получение самого раннего актуального события на текущий момент
            published_events_in_group = events_in_group.filter(event__is_published=True)
            self.value['earliest_published_event_in_group'] = (
                list(published_events_in_group)[0] if
                len(published_events_in_group) > 0 else
                None
            )

            # Получение JSON-настроек события/группы
            self.value['settings'] = (
                json.loads(self.value['settings']) if self.value['settings'] is not None else None
            )

    def cache_postprocessing(self, **kwargs):
        # Получение из строки даты и времени в UTC ('2017-08-31T16:00:00+00:00')
        # В шаблоне она должна локализоваться с учётом текущего часового пояса
        self.value['event_datetime'] = parse(self.value['event_datetime'])

        # Если это группа и в ней есть актуальные события -
        # замена некоторых параметров группы на параметры самого раннего актуального события в ней
        # (при показе "на главной")
        if self.value['is_group'] and self.value['earliest_published_event_in_group'] is not None and self.override:
            debug_console('    override group with event params...')

            # Получение параметров самого раннего актуального события
            earliest_event_cache = EventCache(
                'event', self.value['earliest_published_event_in_group'], override=False).value

            # Если актуальное событие присутствует
            if self.value['earliest_published_event_in_group']:
                for sub in self.substitutes['event_to_group']:
                    debug_console('    ----- ', sub)
                    debug_console('    ----|-from', self.value[sub])
                    debug_console('    ----|---to', earliest_event_cache[sub])
                    self.value[sub] = earliest_event_cache[sub]

            self.override_group_with_event_info = False

        # Если это событие в группе - замена некоторых параметров события на параметры его группы
        # (при выводе события на сайте или при генерации электронных билетов)
        elif self.value['is_in_group'] and self.override:
            debug_console('    override event with group params...')

            # Получение параметров группы
            group_cache = EventCache('group', self.value['group_uuid'], override=False).value

            for sub in self.substitutes['group_to_event']:
                debug_console('    ----- ', sub)
                debug_console('    ----|-from', self.value[sub])
                debug_console('    ----|---to', group_cache[sub])
                self.value[sub] = group_cache[sub]

            self.override_event_with_group_info = False

        # В любом случае  - получение пути к афише в позиции ``small_vertical`` либо заглушки по умолчанию
        # Для событий, принадлежащих одной группе, афиша берётся из группы
        if (self.value['is_group'] or self.value['is_in_group']):
            item_type = 'group'
            item_uuid = self.value['event_uuid'] if self.value['is_group'] else self.value['group_uuid']
        else:
            item_type = 'event'
            item_uuid = self.value['event_uuid']

        poster_path = os.path.join(
            self.value['domain_slug'],
            item_type,
            str(item_uuid)
        )

        poster_file_extensions = ('png', 'jpg', 'jpeg', 'gif',)

        for ext in poster_file_extensions:
            poster_file = 'small_vertical.{ext}'.format(ext=ext)
            # debug_console('    try {poster_path}/{poster_file}'.format(
            #         poster_path=poster_path,
            #         poster_file=poster_file
            #     )
            # )
            if os.path.isfile(os.path.join(settings.MEDIA_ROOT, poster_path, poster_file)):
                self.value['poster'] = '{poster_path}/{poster_file}'.format(
                    poster_path=poster_path,
                    poster_file=poster_file
                )
                # debug_console('    found poster', self.value['poster'])
                break
        else:
            self.value['poster'] = 'global/event/small_vertical.png'.format(
                media_url=settings.MEDIA_URL
            )
            # debug_console('    found default poster', self.value['poster'])
