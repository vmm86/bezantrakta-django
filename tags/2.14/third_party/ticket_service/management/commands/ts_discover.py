import hashlib
import logging
import simplejson as json
import textwrap
import uuid

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Q
from django.db.utils import IntegrityError

from project.shortcuts import datetime_localize_or_utc, timezone_now
from project.urlify import urlify

from bezantrakta.event.cache import event_or_group_cache
from bezantrakta.event.models import Event, EventGroupBinder

from third_party.ticket_service.cache import ticket_service_cache, ticket_service_instance
from third_party.ticket_service.models import TicketService, TicketServiceSchemeVenueBinder


class Command(BaseCommand):
    """Задание для импорта залов, групп и событий из подключенных к сайтам сервисов продажи билетов (СПБ).

    Полученная информация записывается в соответствующие таблицы базы данных (БД).

    Если какой-то shared-СПБ содержит информацию, предназначенную для разных сайтов,
    то запросы к нему делаются *только один раз*, а их результаты добавляются во временный кэш в памяти ``task_cache``.
    Временный кэш в памяти - это словарь (ключи - md5-хэш параметра ``init`` в настройках СПБ;
    значения - тоже словари (ключи - строки ``schemes``, ``groups``, ``events``; значения - результаты соответствующих запросов к определённому СПБ)).
    Другие сайты, подключенные к этому же СПБ, используют ранее полученые данные из ``task_cache``.

    Получаем из БД список сервисов продажи билетов, привязанных к разным сайтам.
    Для каждого из активных СПБ проводятся следующие действия:

    1) Инстанцирование класса СПБ, используя параметры из его настроеки.

    2) Получение и запись в БД списка схем залов СПБ с помощью ``discover_schemes``.

    3) В модель ``TicketServiceSchemeVenueBinder`` записываются:

    * либо все схемы залов СПБ,

    * либо только те схемы залов, ID которых указаны в настройках СПБ в параметре ``schemes``.

    4) Получение групп/событий СПБ с помощью ``discover_groups``/``discover_events``
    происходит только для тех схем залов СПБ, которые предварительно в админ-панели
    были связаны с добавленными вручную залами (местами проведения событий) в модели ``event.EventVenue``.

    5) В БД сохраняются новые группы событий.
    У уже имеющихся обновляется дата/время из самого раннего актуального события.

    6) В БД сохраняются новые события.
    У уже имеющихся обновляется дата/время.

    7) Если событие входит в группу, добавленную или уже имеющуюся,
    событие привязывается к этой группе в self-M2M-модели ``event.EventGroupBinder``.

    Задание должно запускаться в cron с определённой периодичностью:

    ``***** source {venv/biv/activate} && python {корень проекта}/manage.py ts_discover``

    Attributes:
        help (str): Справочная информация о задании.
        logger (Logger): Экземпляр логгера.
        task_cache (dict): Временный кэш задания в памяти.
        group_id_uuid_mapping (dict): Связка идентификаторов групп в СПБ и в БД.
        event_id_uuid_mapping (dict): Связка идентификаторов событий в СПБ и в БД.
        event_model_max_length (int): Максимальное число символов в названии события в модели ``event.Event``
    """
    help = """
Импорт информации из подключенных к сайтам сервисов продажи билетов (СПБ).____
Запись полученной информации в соответствующие таблицы базы данных (БД).______
Получаем из БД список сервисов продажи билетов, привязанных к разным сайтам.__
Если какой-то shared-СПБ содержит информацию для разных сайтов,_______________
то запросы к нему делаются ТОЛЬКО ОДИН РАЗ, а их результаты добавляются_______
во временный кэш в памяти. Другие сайты, подключенные к этому же СПБ,_________
используют ранее полученые данные из временного кэша в памяти.________________
Для каждого из активных сервисов продажи билетов (СПБ) проводится следующее:__
1) Инстанцирование класса СПБ, используя параметры из его настроеки.__________
2) Получение и запись в БД списка схем залов СПБ с помощью `discover_schemes`.
3) В модель `TicketServiceSchemeVenueBinder` записываются:____________________
__ либо все схемы залов СПБ,__________________________________________________
__ либо только схемы залов, ID которых указаны в настройках СПБ в `schemes`.__
4) Получение групп/событий СПБ с помощью `discover_groups`/`discover_events`__
происходит только для схем залов СПБ, которые предварительно в админ-панели___
были связаны с добавленными вручную залами (местами проведения событий)_______
в модели `EventVenue`.________________________________________________________
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
    task_cache = {}
    group_id_uuid_mapping = {}
    event_id_uuid_mapping = {}
    event_model_max_length = Event._meta.get_field('title').max_length

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
                Q(city_state=True) | Q(city_state=None),
                Q(is_active=True),
            )
        )

        if len(active_ticket_services) > 0:
            self.log(
                'Всего найдено {n} активных сервисов продажи билетов\n'.format(n=len(active_ticket_services)),
                level='INFO'
            )

            for ats in active_ticket_services:
                ticket_service = ticket_service_cache(ats['id'])
                ticket_service['timezone'] = ats['city_timezone']

                # Формирование кэша текущего задания в памяти
                # Ключи - md5-хэш, который у параметров подключения к одному и тому же СПБ будет одинаковым
                init_checksum = hashlib.md5(
                    json.dumps(ticket_service['settings']['init'], sort_keys=True).encode('utf-8')
                ).hexdigest()

                if init_checksum not in self.task_cache.keys():
                    self.task_cache[init_checksum] = {}
                    self.task_cache[init_checksum]['schemes'] = None
                    self.task_cache[init_checksum]['groups'] = None
                    self.task_cache[init_checksum]['events'] = None

                # Экземпляр класса сервиса продажи билетов для конкретного сайта
                ts = ticket_service_instance(ats['id'])
                self.log('{ico} {title}'.format(ico='🎫', title=ticket_service['title']), level='INFO')
                self.log('Часовой пояс: {tz}'.format(tz=ticket_service['timezone']))

                # Схемы залов конкретного сервиса продажи билетов
                self.stdout.write('Поиск схем залов сервиса продажи билетов...')
                self.task_cache[init_checksum]['schemes'] = (
                    ts.discover_schemes() if
                    self.task_cache[init_checksum]['schemes'] is None else
                    self.task_cache[init_checksum]['schemes']
                )
                schemes = self.task_cache[init_checksum]['schemes']

                self.stdout.write('Всего найдено {n} схем залов сервиса продажи билетов'.format(n=len(schemes)))

                if settings.DEBUG:
                    self.task_cache_logger(self.task_cache)

                # Возможность добавлять из сервиса продажи билетов только те схемы залов,
                # которые явно принадлежат именно к этому сайту в этом городе
                # (для shared-сервисов продажи билетов между несколькими сайтами).
                schemes_inclusion_list = (
                    ticket_service['settings']['schemes'] if
                    'schemes' in ticket_service['settings'] and
                    type(ticket_service['settings']['schemes']) is list and
                    len(ticket_service['settings']['schemes']) > 0 else
                    None
                )
                if schemes_inclusion_list is None:
                    self.stdout.write('Из сервиса продажи билетов импортируются ВСЕ схемы залов')
                else:
                    self.stdout.write('Из сервиса продажи билетов импортируются только схемы залов {sil}'.format(
                        sil=schemes_inclusion_list)
                    )

                # Содержимое параметра `schemes` добавляется администратором по необходимости
                # и используется, только если этот список - непустой.
                # В противном случае в БД сайта добавляются все схемы залов из сервиса продажи билетов.
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
                                'Добавлена схема зала {id}: {title}'.format(
                                    id=s['scheme_id'],
                                    title=s['scheme_title']
                                ), level='SUCCESS'
                            )

                # Имеющиеся в БД схемы залов из сервиса продажи билетов,
                # связанные ранее с залами (местами проведения событий) в модели ``event.EventVenue``
                ts_scheme_venue_binder = dict(TicketServiceSchemeVenueBinder.objects.filter(
                    ticket_service_id=ticket_service['id'],
                    ticket_service__domain_id=ticket_service['domain_id'],
                    event_venue__isnull=False,
                ).values_list(
                    'ticket_service_scheme_id',
                    'event_venue_id',
                ))

                # Группы и события из сервиса продажи билетов запрашиваются,
                # только если их схемы залов связаны с залами (местами проведения событий) в БД
                if len(ts_scheme_venue_binder) > 0:
                    self.stdout.write('Имеются связки схем залов с залами (местами проведения событий).')

                    # Группы, уже добавленные в БД ранее, к которым могут быть привязаны новые события
                    groups_exist = Event.objects.filter(
                        is_group=True,
                        domain_id=ticket_service['domain_id'],
                        ticket_service_id=ticket_service['id'],
                    ).values(
                        'id',
                        'ticket_service_event',
                    )
                    self.group_id_uuid_mapping = {ge['ticket_service_event']: ge['id'] for ge in groups_exist}
                    self.stdout.write('Имеющиеся группы событий: {}'.format(self.group_id_uuid_mapping))

                    # События, уже добавленные в БД ранее
                    events_exist = Event.objects.filter(
                        is_group=False,
                        domain_id=ticket_service['domain_id'],
                        ticket_service_id=ticket_service['id'],
                    ).values(
                        'id',
                        'ticket_service_event',
                    )
                    self.event_id_uuid_mapping = {ee['ticket_service_event']: ee['id'] for ee in events_exist}
                    self.stdout.write('Имеющиеся события: {}'.format(self.event_id_uuid_mapping))

                    self.stdout.write('Поиск групп событий...')
                    self.task_cache[init_checksum]['groups'] = (
                        ts.discover_groups() if
                        self.task_cache[init_checksum]['groups'] is None else
                        self.task_cache[init_checksum]['groups']
                    )
                    groups = self.task_cache[init_checksum]['groups']

                    self.stdout.write('Поиск событий...')
                    self.task_cache[init_checksum]['events'] = (
                        ts.discover_events() if
                        self.task_cache[init_checksum]['events'] is None else
                        self.task_cache[init_checksum]['events']
                    )
                    events = self.task_cache[init_checksum]['events']

                    if settings.DEBUG:
                        self.task_cache_logger(self.task_cache)

                    # Группы и события фильтруются по схемам залов в schemes_inclusion_list, если параметр присутствует
                    if schemes_inclusion_list is not None:
                        groups = [g for g in groups if g['scheme_id'] in schemes_inclusion_list]
                        events = [e for e in events if e['scheme_id'] in schemes_inclusion_list]

                    # Импорт групп в БД
                    if groups is not None and len(groups) > 0:
                        for group in groups:
                            # Поиск групп
                            self.import_groups(ticket_service, ts_scheme_venue_binder, group)
                    else:
                        self.log('Не найдено ни одной группы событий', level='NOTICE')

                    # Импорт событий в БД
                    if events is not None and len(events) > 0:
                        for event in events:
                            # Поиск событий с возможной привязкой к группам
                            self.import_events(ticket_service, ts, ts_scheme_venue_binder, event)
                    else:
                        self.log('Не найдено ни одного события', level='NOTICE')
                else:
                    self.log('Нет связок схем залов с залами (местами проведения событий)!', level='NOTICE')
                    continue
        else:
            self.log('Не найдено ни одного активного сервиса продажи билетов!', level='ERROR')

    def import_groups(self, ticket_service, ts_scheme_venue_binder, group):
        """Импорт групп из СПБ и их запись в БД.

        Args:
            ticket_service (dict): Информация о СПБ.
            ts_scheme_venue_binder (dict): Схемы залов в БД.
            group (dict): Информация о текущей группе в списке групп.
        """
        # today = timezone_now()
        # В БД сохраняются только те группы,
        # схемы залов у которых были ранее в админ-панели связаны с залами (местами проведения событий) в БД
        if group['scheme_id'] in ts_scheme_venue_binder.keys():
            # Получение даты/времени в текущем часовом поясе (с сохранением в БД в UTC)
            group['group_datetime'] = datetime_localize_or_utc(group['group_datetime'], ticket_service['timezone'])
            # Уникальный идентификатор новой группы
            group_uuid = uuid.uuid4()
            # Название группы НЕ должно быть больше max числа символов, указанного в модели
            group['group_title'] = textwrap.shorten(
                group['group_title'], width=self.event_model_max_length, placeholder='...'
            )
            # Добавление к псевдониму группы идентификатора группы для уникальности
            slug_num_chars = self.event_model_max_length - (len(str(group['group_id'])) + 1)
            group_slug = '{title}-{id}'.format(
                title=urlify(group['group_title'], num_chars=slug_num_chars),
                id=group['group_id'],
            )

            # Если группа уже была добавлена ранее
            if group['group_id'] in self.group_id_uuid_mapping.keys():
                self.stdout.write(
                    'Группа {group_id}: {group_title} была добавлена ранее'.format(
                        group_id=group['group_id'],
                        group_title=group['group_title']
                    )
                )

                # Обновление информации в добавленной ранее группе событий
                upd = Event.objects.filter(
                    id=self.group_id_uuid_mapping[group['group_id']],
                    # datetime__gt=today
                ).update(
                    datetime=group['group_datetime']
                )

                if upd > 0:
                    # Обновить кэш группы при обновлении её данных
                    event_or_group_cache(group_uuid, 'group', reset=True)
                    self.stdout.write(
                        '    Обновлён кэш группы {group_id}: {group_title}'.format(
                            group_id=group['group_id'],
                            group_title=group['group_title']
                        )
                    )
            # Добавление новой группы в БД
            else:
                try:
                    Event.objects.create(
                        id=group_uuid,
                        title=group['group_title'],
                        slug=group_slug,
                        description='',
                        keywords='',
                        text=group['group_text'],
                        is_published=False,
                        is_on_index=False,
                        min_price=group['group_min_price'],
                        datetime=group['group_datetime'],
                        event_venue_id=ts_scheme_venue_binder[group['scheme_id']],
                        domain_id=ticket_service['domain_id'],
                        is_group=True,
                        ticket_service_id=ticket_service['id'],
                        ticket_service_event=group['group_id'],
                        ticket_service_scheme=None,
                    )
                except IntegrityError:
                    pass
                else:
                    self.log(
                        'Добавлена группа {group_id}: {group_title}'.format(
                            group_id=group['group_id'],
                            group_title=group['group_title']
                        ), level='SUCCESS'
                    )

                    self.group_id_uuid_mapping[group['group_id']] = group_uuid

                    # В любом случае обновить кэш группы
                    event_or_group_cache(group_uuid, 'group')
                    self.stdout.write(
                        '    Создан кэш группы {group_id}: {group_title}'.format(
                            group_id=group['group_id'],
                            group_title=group['group_title']
                        )
                    )

    def import_events(self, ticket_service, ts, ts_scheme_venue_binder, event):
        """Импорт событий из СПБ и их запись в БД (при наличии групп или при их отсутствии).

        При наличии групп событие может быть привязано у группе, к которой оно принадлежит.

        Список цен получаем здесь, а не в самом методе ``dicover_events`` в классе СПБ,
        поскольку по крайней мере в СуперБилете это будет занимать очень долгое время...

        Args:
            ticket_service (dict): Информация о СПБ.
            ts (TicketSrvice): Экземпляр класса СПБ.
            ts_scheme_venue_binder (dict): Схемы залов в БД.
            event (dict): Информация о текущем событии в списке событий.
        """
        today = timezone_now()
        # В БД сохраняются только те события,
        # схемы залов у которых связаны с залами (местами проведения событий) в БД
        if event['scheme_id'] in ts_scheme_venue_binder.keys():
            # Получение даты/времени в текущем часовом поясе (с сохранением в БД в UTC)
            event['event_datetime'] = datetime_localize_or_utc(
                event['event_datetime'], ticket_service['timezone']
            )
            # Название события НЕ должно быть больше max числа символов, указанного в модели
            event['event_title'] = textwrap.shorten(
                event['event_title'], width=self.event_model_max_length, placeholder='...'
            )
            # Добавление к псевдониму события идентификатора события для уникальности
            slug_num_chars = self.event_model_max_length - (len(str(event['event_id'])) + 1)
            event_slug = '{title}-{id}'.format(
                title=urlify(event['event_title'], num_chars=slug_num_chars),
                id=event['event_id'],
            )
            # Получение списка цен на билеты (для легенды схемы зала)
            seats_and_prices = ts.seats_and_prices(event_id=event['event_id'])
            # Минимальная цена на билет берётся из списка цен,
            # если список цен непустой и если минимальная цена отсутствует или равна 0
            if len(seats_and_prices) > 0 and len(seats_and_prices['prices']) > 0 and event['event_min_price'] == 0:
                event['event_min_price'] = seats_and_prices['prices'][0]

            # Если событие уже было добавлено ранее
            if event['event_id'] in self.event_id_uuid_mapping.keys():
                event_uuid = self.event_id_uuid_mapping[event['event_id']]
                self.stdout.write(
                    'Событие {event_id}: {event_title} было добавлено ранее'.format(
                        event_id=event['event_id'],
                        event_title=event['event_title']
                    )
                )

                # Обновление информации в добавленном ранее событии
                upd = Event.objects.filter(
                    id=self.event_id_uuid_mapping[event['event_id']],
                    datetime__gt=today
                ).update(
                    datetime=event['event_datetime'],
                    min_price=event['event_min_price'],
                )

                if upd > 0:
                    # Обновить кэш события при обновлении его данных
                    event_or_group_cache(event_uuid, 'event', reset=True)
                    self.stdout.write(
                        '    Обновлён кэш события {event_id}: {event_title}'.format(
                            event_id=event['event_id'],
                            event_title=event['event_title']
                        )
                    )
            # Добавление нового события в БД
            else:
                # Уникальный идентификатор нового события
                event_uuid = uuid.uuid4()
                try:
                    Event.objects.create(
                        id=event_uuid,
                        title=event['event_title'],
                        slug=event_slug,
                        description='',
                        keywords='',
                        text=event['event_text'],
                        is_published=False,
                        is_on_index=False,
                        min_price=event['event_min_price'],
                        min_age=event['event_min_age'],
                        datetime=event['event_datetime'],
                        event_venue_id=ts_scheme_venue_binder[event['scheme_id']],
                        domain_id=ticket_service['domain_id'],
                        is_group=False,
                        ticket_service_id=ticket_service['id'],
                        ticket_service_event=event['event_id'],
                        ticket_service_scheme=event['scheme_id'],
                    )
                except IntegrityError:
                    pass
                else:
                    self.log(
                        'Добавлено событие {event_id}: {event_title}'.format(
                            event_id=event['event_id'],
                            event_title=event['event_title']
                        ), level='SUCCESS'
                    )

                # Если событие принадлежит ранее добавленной в БД группе -
                # событие привязывается к этой группе.
                if event['group_id'] in self.group_id_uuid_mapping.keys():
                    try:
                        EventGroupBinder.objects.create(
                            group_id=self.group_id_uuid_mapping[event['group_id']],
                            event_id=event_uuid,
                        )
                    except IntegrityError:
                        pass
                    else:
                        group_info = event_or_group_cache(self.group_id_uuid_mapping[event['group_id']], 'group')
                        self.log(
                            'Событие {event_id}: {event_title} привязано к группе {group_id}: {group_title}'.format(
                                    event_id=event['event_id'],
                                    event_title=event['event_title'],
                                    group_id=group_info['ticket_service_event'],
                                    group_title=group_info['event_title']
                            ), level='SUCCESS'
                        )

                        # Создать кэш нового события в БД
                        event_or_group_cache(event_uuid, 'event')
                        self.stdout.write(
                            '    Создан кэш события {event_id}: {event_title}'.format(
                                event_id=event['event_id'],
                                event_title=event['event_title']
                            )
                        )

    def log(self, msg, level=None):
        """Метод для логирования информации и в консоль, и в лог-файл.

        При логировании в консоль текст может быть отформатирован в зависимости от опционального статуса.
        При логировании в лог-файл опциональный статус указывается текстом.

        Args:
            msg (str): Текстовое сообщение.
            level (str, optional): Опциональный статус (уровень) сообщения.
        """
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

    def task_cache_logger(self, task_cache):
        """Логирование в консоль прогресса формирования временного кэша в памяти ``task_cache``.

        Выводится при выполении задания в консоли только в development-версии проекта.

        Получаемые списки залов, групп и событий обрезаются до первого элемента списка для экономии места на экране.

        Args:
            task_cache (dict): Временный кэш выполняемого задания в памяти.
        """
        self.stdout.write(self.style.SUCCESS('\n{ task_cache }'))

        # Сущности, запросы на импорт которых необходимо кэшировать при обращении к СПБ
        discover_requests = ('schemes', 'groups', 'events')

        for init_checksum in task_cache.keys():
            self.stdout.write(self.style.WARNING('|'))
            self.stdout.write(self.style.WARNING('|- init_checksum: {}'.format(init_checksum)))

            for request in discover_requests:
                response = (
                    '[{}, ...]'.format(task_cache[init_checksum][request][0]) if
                    task_cache[init_checksum][request] else
                    task_cache[init_checksum][request]
                )
                self.stdout.write('   |-  {request}: {response}'.format(request=request, response=response))

        self.stdout.write('\n')
