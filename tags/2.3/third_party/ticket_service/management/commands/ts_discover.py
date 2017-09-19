import logging
import simplejson as json
import uuid

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.db.utils import IntegrityError

from project.shortcuts import datetime_localize_or_utc, timezone_now
from project.urlify import urlify

from bezantrakta.event.cache import get_or_set_cache as get_or_set_event_cache
from bezantrakta.event.models import Event, EventGroupBinder

from third_party.ticket_service.cache import get_or_set_cache as get_or_set_ticket_service_cache
from third_party.ticket_service.cache import ticket_service_instance
from third_party.ticket_service.models import TicketService, TicketServiceSchemeVenueBinder


class Command(BaseCommand):
    """Задание для импорта информации из подключенных к сайтам сервисов продажи билетов.

    Поиск залов, групп и событий в подключенных к сайтам билетных сервисах.
    Запись полученной информации в соответствующие таблицы базы данных.
    Получаем из БД список сервисов продажи билетов, привязанных к разным сайтам.

    Для каждого из активных сервисов продажи билетов (СПБ) проводятся следующие действия:

    1) Инстанцирование класса СПБ, используя параметры из его настроеки.

    2) Получение и запись в БД списка залов СПБ с помощью ``discover_schemes``.

    3) В модель ``TicketServiceSchemeVenueBinder`` записываются:

    * либо все залы СПБ,

    * либо только залы, ID которых указаны в настройках СПБ в параметре ``schemes``.

    4) Получение групп/событий СПБ с помощью ``discover_groups``/``discover_events``
    происходит только для тех залов СПБ, которые предварительно в админ-панели
    были связаны с уникальными добавленными вручную залами в модели ``event.EventVenue``.

    5) В БД сохраняются новые группы событий.
    У уже имеющихся обновляется дата/время из самого раннего актуального события.

    6) В БД сохраняются новые события.
    У уже имеющихся обновляется дата/время.

    7) Если событие входит в группу, добавленную или уже имеющуюся,
    событие привязывается к этой группе в self-M2M-модели ``event.EventGroupBinder``.

    Задание должно запускаться в cron с определённой периодичностью:

    ``***** source {venv/biv/activate} && python {корень проекта}/manage.py ts_discover``
    """
    help = """
Поиск залов, групп и событий в подключенных к сайтам билетных сервисах._______
Запись полученной информации в соответствующие таблицы базы данных.___________
Получаем из БД список сервисов продажи билетов, привязанных к разным сайтам.__
Для каждого из активных сервисов продажи билетов (СПБ) проводится следующее:__
1) Инстанцирование класса СПБ, используя параметры из его настроеки.__________
2) Получение и запись в БД списка залов СПБ с помощью `discover_schemes`._____
3) В модель `TicketServiceSchemeVenueBinder` записываются:__________________________
__ либо все залы СПБ,_________________________________________________________
__ либо только залы, ID которых указаны в настройках СПБ в свойстве `schemes`.
4) Получение групп/событий СПБ с помощью `discover_groups`/`discover_events`__
происходит только для тех залов СПБ, которые предварительно в админ-панели____
были связаны с уникальными добавленными вручную залами в модели `EventVenue`._
5) В БД сохраняются новые группы событий._____________________________________
У уже имеющихся обновляется дата/время из самого раннего актуального события._
6) В БД сохраняются новые события.____________________________________________
У уже имеющихся обновляется дата/время._______________________________________
7) Если событие входит в группу, добавленную или уже имеющуюся,_______________
событие привязывается к этой группе в self-M2M-модели `EventGroupBinder`._____
______________________________________________________________________________
Задание должно запускаться в cron с определённой периодичностью:______________
***** source {venv/biv/activate} && python {корень проекта}/manage.py command
    """
    logger = logging.getLogger('ticket_service.discover')

    def log(self, msg, level=None):
        if level is None:
            self.stdout.write(msg)
            self.logger.info(msg)
        else:
            if level == 'INFO':
                self.stdout.write(self.style.WARNING(msg))
                self.logger.info('[INFO] {}'.format(msg))
            elif level == 'SUCCESS':
                self.stdout.write(self.style.SUCCESS(msg))
                self.logger.info('[SUCCESS] {}'.format(msg))
            elif level == 'NOTICE':
                self.stdout.write(self.style.NOTICE(msg))
                self.logger.error('[NOTICE] {}'.format(msg))
            elif level == 'ERROR':
                self.stdout.write(self.style.ERROR(msg))
                self.logger.critical('[ERROR] {}'.format(msg))

    def handle(self, *args, **options):
        now = timezone_now()

        self.logger.info('\n--------------------------------------------------')
        self.logger.info('{:%Y-%m-%d %H:%M:%S}'.format(now))
        self.stdout.write('Поиск активных сервисов продажи билетов...')

        active_ticket_services = list(
            TicketService.objects.select_related(
                'domain',
            ).annotate(
                city_state=F('domain__city__state'),
                city_timezone=F('domain__city__timezone'),
            ).values(
                'id',
                'city_state',
                'city_timezone',
            ).filter(
                Q(is_active=True),
                Q(city_state=True) | Q(city_state=None),
            )
        )

        if len(active_ticket_services) > 0:
            self.log(
                'Найдено {n} активных сервисов продажи билетов.\n'.format(n=len(active_ticket_services)),
                level='INFO'
            )

            for ats in active_ticket_services:
                ticket_service = get_or_set_ticket_service_cache(ats['id'])

                current_timezone = ats['city_timezone']

                # Экземпляр класса сервиса продажи билетов для конкретного сайта
                ts = ticket_service_instance(ats['id'])
                self.log('{ico} {title}'.format(ico='🎫', title=ticket_service['title']), level='INFO')
                self.log('Часовой пояс: {tz}'.format(tz=current_timezone))

                # Залы конкретного сервиса продажи билетов
                self.stdout.write('Поиск залов сервиса продажи билетов...')
                schemes = ts.discover_schemes()
                self.stdout.write('Найдено {n} схем залов сервиса продажи билетов'.format(n=len(schemes[0])))

                # Возможность добавлять из сервиса продажи билетов только те его залы,
                # которые явно принадлежат именно к этому сайту в этом городе
                # (для shared-билетных сервисов между несколькими сайтами).
                schemes_inclusion_list = (
                    ticket_service['settings']['schemes'] if
                    'schemes' in ticket_service['settings'] and
                    type(ticket_service['settings']['schemes']) is list and
                    len(ticket_service['settings']['schemes']) > 0 else
                    None
                )
                if schemes_inclusion_list is None:
                    self.stdout.write('Из сервиса продажи билетов импортируются ВСЕ залы')
                else:
                    self.stdout.write('Из сервиса продажи билетов импортируются только залы {vil}'.format(
                        vil=schemes_inclusion_list)
                    )

                # Содержимое параметра `schemes` добавляется администратором по необходимости
                # и используется, только если этот список - непустой.
                # В противном случае в БД сайта добавляются все залы из сервиса продажи билетов.
                for s in schemes:
                    if (
                        schemes_inclusion_list is None or
                        (
                            schemes_inclusion_list is not None and
                            s['scheme_id'] in schemes_inclusion_list
                        )
                    ):
                        try:
                            TicketServiceSchemeVenueBinder.objects.create(
                                ticket_service_id=ticket_service['id'],
                                ticket_service_scheme_id=s['scheme_id'],
                                ticket_service_scheme_title=s['scheme_title'],
                            )
                        except IntegrityError:
                            pass
                        else:
                            self.log(
                                'Добавлена связка со схемой зала сервиса продажи билетов {id}: {title}'.format(
                                    id=s['scheme_id'],
                                    title=s['scheme_title']
                                ), level='SUCCESS'
                            )

                # Схемы залов из сервиса продажи билетов, связанные ранее с залами в модели ``event.EventVenue``
                ts_scheme_venue_binder = dict(TicketServiceSchemeVenueBinder.objects.filter(
                    ticket_service_id=ticket_service['id'],
                    ticket_service__domain_id=ticket_service['domain_id'],
                    event_venue__isnull=False,
                ).values_list(
                    'ticket_service_scheme_id',
                    'event_venue_id',
                ))

                # Группы и события из сервиса продажи билетов зарашиваются,
                # только если их залы в сервисе продажи билетов связаны с залами в БД
                if len(ts_scheme_venue_binder) > 0:
                    # Сохранение групп в БД
                    self.stdout.write('Имеются связки залов с сервисами продажи билетов.')

                    # Группы, уже добавленные в БД ранее, к которым могут быть привязаны новые события
                    groups_exist = Event.objects.filter(
                        is_group=True,
                        domain_id=ticket_service['domain_id'],
                        ticket_service_id=ticket_service['id'],
                    ).values(
                        'id',
                        'ticket_service_event',
                    )
                    group_id_uuid_mapping = {ge['ticket_service_event']: ge['id'] for ge in groups_exist}
                    self.stdout.write('Имеющиеся группы событий: {}'.format(group_id_uuid_mapping))

                    # События, уже добавленные в БД ранее
                    events_exist = Event.objects.filter(
                        is_group=False,
                        domain_id=ticket_service['domain_id'],
                        ticket_service_id=ticket_service['id'],
                    ).values(
                        'id',
                        'ticket_service_event',
                    )
                    events_id_uuid_mapping = {ee['ticket_service_event']: ee['id'] for ee in events_exist}
                    self.stdout.write('Имеющиеся события: {}'.format(events_id_uuid_mapping))

                    self.stdout.write('Поиск групп событий...')
                    groups = ts.discover_groups()

                    self.stdout.write('Поиск событий...')
                    events = ts.discover_events()

                    if groups is not None and len(groups) > 0:
                        # Сохранение групп в БД

                        # В БД сохраняются только те группы,
                        # залы в сервисе продажи билетов у которых связаны с залами в БД.
                        for g in groups:
                            if g['scheme_id'] in ts_scheme_venue_binder.keys():
                                # Получение даты/времени в текущем часовом поясе (с сохранением в БД в UTC)
                                g['group_datetime'] = datetime_localize_or_utc(g['group_datetime'], current_timezone)
                                group_uuid = uuid.uuid4()
                                # Добавление к псевдониму группы идентификатора группы для уникальности
                                slug_num_chars = 64 - (len(str(g['group_id'])) + 1)
                                group_slug = '{title}-{id}'.format(
                                    title=urlify(g['group_title'], num_chars=slug_num_chars),
                                    id=g['group_id'],
                                )

                                # Если группа событий уже была добавлена ранее
                                if g['group_id'] in group_id_uuid_mapping.keys():
                                    self.stdout.write(
                                        'Группа событий {gid} была добавлена ранее'.format(gid=g['group_id'])
                                    )
                                    # Обновление информации в добавленной ранее группе событий
                                    Event.objects.filter(
                                        id=group_id_uuid_mapping[g['group_id']]
                                    ).update(
                                        datetime=g['group_datetime']
                                    )
                                else:
                                    try:
                                        Event.objects.create(
                                            id=group_uuid,
                                            title=g['group_title'],
                                            slug=group_slug,
                                            description='',
                                            keywords='',
                                            text=g['group_text'],
                                            is_published=False,
                                            is_on_index=False,
                                            min_price=g['group_min_price'],
                                            datetime=g['group_datetime'],
                                            event_venue_id=ts_scheme_venue_binder[g['scheme_id']],
                                            domain_id=ticket_service['domain_id'],
                                            is_group=True,
                                            ticket_service_id=ticket_service['id'],
                                            ticket_service_event=g['group_id'],
                                            ticket_service_prices=None,
                                            ticket_service_scheme=None,
                                        )
                                    except IntegrityError:
                                        pass
                                    else:
                                        self.log(
                                            'Добавлена группа событий {id}: {title}'.format(
                                                id=g['group_id'],
                                                title=g['group_title']
                                            ), level='SUCCESS'
                                        )
                                        group_id_uuid_mapping[g['group_id']] = group_uuid

                        # Сохранение событий в БД
                        if events is None and len(events) > 0:
                            self.log('Не найдено ни одного события.', level='NOTICE')
                        else:
                            for e in events:
                                # В БД сохраняются только те события,
                                # залы в сервисе продажи билетов у которых связаны с залами в БД.
                                if e['scheme_id'] in ts_scheme_venue_binder.keys():
                                    # Получение даты/времени в текущем часовом поясе (с сохранением в БД в UTC)
                                    e['event_datetime'] = datetime_localize_or_utc(
                                        e['event_datetime'], current_timezone
                                    )
                                    # Добавление к псевдониму события идентификатора события для уникальности
                                    slug_num_chars = 64 - (len(str(e['event_id'])) + 1)
                                    event_slug = '{title}-{id}'.format(
                                        title=urlify(e['event_title'], num_chars=slug_num_chars),
                                        id=e['event_id'],
                                    )
                                    # Список цен на билеты для легенды схемы зала
                                    prices = ts.prices(event_id=e['event_id'])
                                    # При отсутствии минимальная цена на билет берётся из списка цен
                                    e['event_min_price'] = (
                                        prices[0] if
                                        e['event_min_price'] == 0 and len(prices) > 0 else
                                        0
                                    )

                                    # Если событие уже было добавлено ранее
                                    if e['event_id'] in events_id_uuid_mapping.keys():
                                        event_uuid = events_id_uuid_mapping[e['event_id']]
                                        self.stdout.write(
                                            'Событие {eid} было добавлено ранее'.format(eid=e['event_id'])
                                        )
                                        # Обновление информации в добавленном ранее событии
                                        Event.objects.filter(
                                            id=events_id_uuid_mapping[e['event_id']]
                                        ).update(
                                            datetime=e['event_datetime'],
                                        )
                                    else:
                                        event_uuid = uuid.uuid4()
                                        try:
                                            Event.objects.create(
                                                id=event_uuid,
                                                title=e['event_title'],
                                                slug=event_slug,
                                                description='',
                                                keywords='',
                                                text=e['event_text'],
                                                is_published=False,
                                                is_on_index=False,
                                                min_price=e['event_min_price'],
                                                min_age=e['event_min_age'],
                                                datetime=e['event_datetime'],
                                                event_venue_id=ts_scheme_venue_binder[e['scheme_id']],
                                                domain_id=ticket_service['domain_id'],
                                                is_group=False,
                                                ticket_service_id=ticket_service['id'],
                                                ticket_service_event=e['event_id'],
                                                ticket_service_prices=json.dumps(prices),
                                                ticket_service_scheme=e['scheme_id'],
                                            )
                                        except IntegrityError:
                                            pass
                                        else:
                                            self.log(
                                                'Добавлено событие {id}: {title}'.format(
                                                    id=e['event_id'],
                                                    title=e['event_title']
                                                ), level='SUCCESS'
                                            )

                                        # Если событие принадлежит ранее добавленной группе -
                                        # событие привязывается к группе в БД
                                        if e['group_id'] in group_id_uuid_mapping.keys():
                                            try:
                                                EventGroupBinder.objects.create(
                                                    group_id=group_id_uuid_mapping[e['group_id']],
                                                    event_id=event_uuid,
                                                )
                                            except IntegrityError:
                                                pass
                                            else:
                                                self.log(
                                                    'Событие {event_id}: {event_title} привязано к группе {group_id}: {group_title}'.format(
                                                            event_id=e['event_id'],
                                                            event_title=e['event_title'],
                                                            group_id=g['group_id'],
                                                            group_title=g['group_title']
                                                    ), level='SUCCESS'
                                                )
                                    # В любом случае пересоздать кэш события
                                    get_or_set_event_cache(event_uuid, reset=True)
                                    self.stdout.write(
                                        'Пересоздан кэш события {eid}'.format(eid=e['event_id'])
                                    )
                    else:
                        self.log('Не найдено ни одной группы событий.', level='NOTICE')

                        # Сохранение событий в БД
                        if events is None and len(events) > 0:
                            self.log('Не найдено ни одного события.', level='NOTICE')
                        else:
                            for e in events:
                                # В БД сохраняются только те события,
                                # залы в сервисе продажи билетов у которых связаны с залами в БД.
                                if e['scheme_id'] in ts_scheme_venue_binder.keys():
                                    # Получение даты/времени в текущем часовом поясе (с сохранением в БД в UTC)
                                    e['event_datetime'] = datetime_localize_or_utc(
                                        e['event_datetime'], current_timezone
                                    )
                                    # Добавление к псевдониму события идентификатора события для уникальности
                                    slug_num_chars = 64 - (len(str(e['event_id'])) + 1)
                                    event_slug = '{title}-{id}'.format(
                                        title=urlify(e['event_title'], num_chars=slug_num_chars),
                                        id=e['event_id'],
                                    )
                                    # Список цен на билеты для легенды схемы зала
                                    prices = ts.prices(event_id=e['event_id'])
                                    # При отсутствии минимальная цена на билет берётся из списка цен
                                    e['event_min_price'] = (
                                        prices[0] if
                                        e['event_min_price'] == 0 and len(prices) > 0 else
                                        0
                                    )

                                    # Если событие уже было добавлено ранее
                                    if e['event_id'] in events_id_uuid_mapping.keys():
                                        event_uuid = events_id_uuid_mapping[e['event_id']]
                                        self.stdout.write(
                                            'Событие {eid} было добавлено ранее...'.format(eid=e['event_id'])
                                        )
                                        # Обновление информации в добавленном ранее событии
                                        Event.objects.filter(
                                            id=events_id_uuid_mapping[e['event_id']]
                                        ).update(
                                            datetime=e['event_datetime'],
                                        )
                                    else:
                                        event_uuid = uuid.uuid4()
                                        try:
                                            Event.objects.create(
                                                id=event_uuid,
                                                title=e['event_title'],
                                                slug=event_slug,
                                                description='',
                                                keywords='',
                                                text=e['event_text'],
                                                is_published=False,
                                                is_on_index=False,
                                                min_price=e['event_min_price'],
                                                min_age=e['event_min_age'],
                                                datetime=e['event_datetime'],
                                                event_venue_id=ts_scheme_venue_binder[e['scheme_id']],
                                                domain_id=ticket_service['domain_id'],
                                                is_group=False,
                                                ticket_service_id=ticket_service['id'],
                                                ticket_service_event=e['event_id'],
                                                ticket_service_prices=json.dumps(prices),
                                                ticket_service_scheme=e['scheme_id'],
                                            )
                                        except IntegrityError:
                                            pass
                                        else:
                                            self.log(
                                                'Добавлено событие {id}: {title}'.format(
                                                    id=e['event_id'],
                                                    title=e['event_title']
                                                ), level='SUCCESS'
                                            )
                                    # В любом случае пересоздать кэш события
                                    get_or_set_event_cache(event_uuid, reset=True)
                                    self.stdout.write(
                                        'Пересоздан кэш события {eid}'.format(eid=e['event_id'])
                                    )
                else:
                    self.log('Нет связок залов с сервисами продажи билетов!', level='NOTICE')
                    continue
        else:
            self.log('Не найдено ни одного активного сервиса продажи билетов!', level='ERROR')
