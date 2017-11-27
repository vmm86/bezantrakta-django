from dateutil.parser import parse
import os

from django.conf import settings
from django.db.models import F
from django.urls.base import reverse

from project.cache import ProjectCache
from project.shortcuts import build_absolute_url, debug_console, humanize_date

from ..models import Event


class EventCache(ProjectCache):
    entities = ('event', 'group', )
    model = Event

    def get_model_object(self, object_id):
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
                is_in_group=F('event_groups'),
                # Параметры группы, если событие в неё входит
                group_uuid=F('event_groups'),

                payment_service_id=F('ticket_service__payment_service__id'),

                domain_slug=F('domain__slug'),

                city_timezone=F('domain__city__timezone'),
            ).values(
                'is_published',
                'is_on_index',
                'is_group',
                'is_in_group',

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

                'group_uuid',

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
        self.value['is_in_group'] = True if self.value['is_in_group'] is not None else False

        # Приведение часового пояса города к str перед кэшированием во избежание исключения
        self.value['city_timezone'] = str(self.value['city_timezone'])

    def cache_postprocessing(self, **kwargs):
        # Получение из строки даты и времени в UTC ('2017-08-31T16:00:00+00:00')
        # В шаблоне она должна локализоваться с учётом текущего часового пояса
        self.value['event_datetime'] = parse(self.value['event_datetime'])

        # Замена некоторых параметров события на параметры родительской группы, если событие в неё входит
        if self.value['is_in_group']:
            # debug_console('    group params overriding...')

            # Получение параметров группы
            group_cache = EventCache('group', self.value['group_uuid']).value

            # Параметры события для замены
            group_substitutes = (
                'event_title',
                'event_min_age',
                'event_description',
                'event_text',
                'event_category_slug',
                'event_category_title',
            )

            for sub in group_substitutes:
                self.value[sub] = group_cache[sub]
                # debug_console('    ----- ', sub)

        # Получение пути к афише в позиции `small_vertical` либо заглушки по умолчанию
        # Для событий, принадлежащих одной группе, афиша берётся из группы
        if (self.value['is_group'] or self.value['is_in_group']):
            item_type = 'group'
            item_uuid = self.value['group_uuid']
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
            # debug_console('    try', ext)
            poster_file = 'small_vertical.{ext}'.format(ext=ext)
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
