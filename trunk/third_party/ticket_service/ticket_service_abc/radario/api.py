import dateutil.parser
import logging
import requests
import simplejson as json
import uuid
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from operator import itemgetter

try:
    from project.shortcuts import BOOLEAN_VALUES
except ImportError:
    BOOLEAN_VALUES = BOOLEAN_VALUES = ('True', 'true', 1, '1', 'y', 'yes', 'д', 'да',)

from ..abc import TicketService


class Radario(TicketService):
    """Класс для работы с API Радарио.

    Любой метод, делающий запросы к API, вызывает для этого конструктор запросов ``request``.

    `Документация по API Радарио версии 1.1 <http://docs.radario.ru/api/>`_.

    При отправке данных используется формат ``application/json`` с соответствующимо заголовком ``Content-Type``.

    Атрибуты класса:
        slug (str): Псевдоним для инстанцирования класса (``radario``).
        logger (logging.Logger): Объект для логирования информации о работе класса.
        bar_code_length (int): Длина штрих-кода.
    """
    slug = 'radario'
    logger = logging.getLogger('ticket_service.radario')

    bar_code_length = 12

    def __init__(self, init):
        """Конструктор класса.

        Args:
            init (dict): Словарь с параметрами для инстанцирования класса.
        """
        super().__init__()

        # Параметры подключения
        self.__api_version = init['api_version']
        self.__api_base_url = 'https://api.radario.ru'
        self.__api_id = init['api_id']
        self.__api_key = init['api_key']
        self.city_id = init['city_id']
        self.company_id = init['company_id']
        self.company_title = init['company_title']

        # Параметры вывода
        self.limit = 100
        self.offset = 0
        self.time_to_live = 15

    def __str__(self):
        return '{cls}(api_version: {api_version}, city: {city}, company: {company_title})'.format(
            cls=self.__class__.__name__,
            api_version=self.__api_version,
            city=self.city_id,
            company_title=self.company_title,
        )

    def request(self, method, url, data, output_mapping, test=False):
        """Конструктор запросов к API.

        Args:
            method (str): HTTP-метод (``GET`` или ``POST``).
            url (str): Относительный URL конкретного метода API.
            data (dict): Параметры запроса для ``GET`` или тело запроса для ``POST``.
            output_mapping (dict): Сопоставление выходных параметров.
            test (bool, optional): Опциональный параметр для тестирования работы.

        Returns:
            list, dict: Обработанный ответ конкретного метода API.
        """
        url_path = self.__api_base_url + url
        # print('request url: ', url_path)

        headers = {
            'api-version': str(self.__api_version),
            'api-id':      str(self.__api_id),
            'api-key':     str(self.__api_key),
        }
        # print('headers: ', headers)

        session = requests.Session()

        if method == 'GET':
            response = session.get(url_path, params=data, headers=headers)
        elif method == 'POST':
            response = session.post(url_path, json=data, headers=headers)

        # print('\n')
        # print('response: ', response.json())
        # print('\n')

        # Если тестируем работу метода - получаем JSON-ответ без обработки
        if test:
            return response.json()
        else:
            return self.prettify_response(response.json(), output_mapping)

    def prettify_response(self, response, output_mapping):
        """Конвертация ответа в структуру данных Python и последующая обработка.

        Args:
            response (dict): Ответ конкретного метода API.
            output_mapping (dict): Словарь для замены.

        Returns:
            list, dict: Обработанный ответ конкретного метода API.
        """
        response_success = True if 'success' in response and response['success'] else False
        if 'error' in response and response['error']:
            response_code = response['error'].get('errorCode', 0)
            response_message = response['error'].get('message', 'OK')
        else:
            response_code = response.get('ErrorCode', 0)
            response_message = response.get('Message', 'OK')

        # Если ответ успешен
        if response_success:
            # Тело ответа с необходимыми данными, либо сообщение об успешном или НЕуспешном ответе
            if 'data' in response:
                if 'items' in response['data']:
                    iterable = response['data']['items']
                elif 'order' in response['data']:
                    iterable = response['data']['order']
                else:
                    iterable = response['data']
            else:
                if response['success']:
                    return {'success': True, }
                else:
                    return {'success': False, 'code': response_code, 'message': response_message, }

            # Если в ответе - множество записей
            if isinstance(iterable, list):
                # Конвертация ключей в человекопонятные значения
                for item in iterable:
                    self.humanize_with_type_casting(item, output_mapping)
            # Если в ответе - одна запись
            elif isinstance(iterable, dict):
                # Конвертация ключей в человекопонятные значения
                self.humanize_with_type_casting(iterable, output_mapping)
                iterable['success'] = True
            return iterable
        # Если ответ НЕуспешен
        else:
            return {'success': False, 'code': response_code, 'message': response_message, }

    def humanize_with_type_casting(self, iterable, output_mapping):
        """Конвертация ключей в необходимые значения и приведение типов данных.

        Args:
            iterable (dict): Ответ метода.
            output_mapping (dict): Словарь для замены.
        """
        for external, internal in output_mapping.items():
            if external in iterable:
                # НЕнужные на выходе записи удаляются из ответа
                if internal is None:
                    iterable.pop(external)
                # Нужные на выходе записи пересохраняются в требуемые ключи из output_mapping
                else:
                    iterable[internal.key] = iterable.pop(external)

                    # Если получено пустое значение - поиск значения по умолчанию
                    if iterable[internal.key] is None:
                        if internal.default_value is not None:
                            iterable[internal.key] = internal.default_value
                    # Если получено НЕпустое значение - приведение типов данных
                    else:
                        if internal.type is str and not isinstance(iterable[internal.key], str):
                            iterable[internal.key] = str(internal.default_value)
                            # Если получена пустая строка - поиск значения по умолчанию
                            iterable[internal.key] == (
                                internal.default_value if
                                iterable[internal.key] == '' and internal.default_value is not None else
                                iterable[internal.key]
                            )
                        elif internal.type is int and not isinstance(iterable[internal.key], int):
                            iterable[internal.key] = int(iterable[internal.key])
                        elif internal.type is bool and not isinstance(iterable[internal.key], bool):
                            iterable[internal.key] = True if iterable[internal.key] in BOOLEAN_VALUES else False
                        elif internal.type is Decimal and not isinstance(iterable[internal.key], Decimal):
                            iterable[internal.key] = self.decimal_price(iterable[internal.key])
                        elif internal.type is datetime and not isinstance(iterable[internal.key], datetime):
                            # '2017-09-29T16:00:00.000+00:00'
                            iterable[internal.key] = dateutil.parser.parse(iterable[internal.key])
                        # Приведение ключей списка из словарей к нижнему регистру
                        elif internal.type is list and isinstance(iterable[internal.key][0], dict):
                            iterable[internal.key] = [
                                {k.lower(): v for k, v in i.items()} for i in iterable[internal.key]
                            ]
                        # Приведение ключей словаря к нижнему регистру
                        elif internal.type is dict:
                            iterable[internal.key] = {k.lower(): v for k, v in iterable[internal.key].items()}
                        else:
                            pass

    def version(self):
        """Версия API Радарио.

        Returns:
            str: Версия API Радарио.
        """
        return self.__api_version

    def places(self):
        """Места проведения событий (в конкретном городе).

        Returns:
            list: Список словарей с информацией о месте проведения событий.
        """
        method = 'GET'
        url = '/places'
        data = {
            'cityId': self.city_id,
            'limit': self.limit,
        }
        if self.__api_version == 1:
            data['onlyWithOrderCreationAvailableViaApi'] = True
        output_mapping = {
            # Идентификатор места
            'id':    self.internal('place_id', int,),
            # Название места
            'title': self.internal('place_title', str,),

            'address':   None,
            'cityId':    None,
            'cityName':  None,
            'latitude':  None,
            'longitude': None,
        }
        places = self.request(method, url, data, output_mapping)

        if isinstance(places, list) and places:
            places = sorted(places, key=itemgetter('place_id'))

        return places

    def scheme(self, **kwargs):
        """Информация о схеме зала в месте проведения событий.

        Ответ в том числе содержит информацию о секторах ("зонах" в терминологии Радарио) и их местах.

        Args:
            scheme_id (int): Идентификатор схемы зала.
            raw (bool, optional): Опциональная возможность получения *schema raw descriptor*.

        Returns:
            dict: Информация о конкретной схеме зала.
        """
        method = 'GET'
        url = '/schemes/{scheme_id}'.format(scheme_id=kwargs['scheme_id'])
        if 'raw' in kwargs and kwargs['raw']:
            url += '/raw'
        data = None
        output_mapping = {
            # Идентификатор зала
            'id':      self.internal('scheme_id', int,),
            # Название зала
            'name':    self.internal('scheme_title', str,),
            # Версия схемы зала
            'version': self.internal('scheme_version', int,),
            # Секторы (зоны) зала
            'zones':   self.internal('scheme_zones', list,),
            # Атрибуты `zones`
            # 'colcount' (int): (?)
            # 'id' (int): Идентификатор сектора
            # 'name' (str): Название сектора
            # 'withseats' (bool): Сектор с местами для сидения или нет
            # 'rowcount' (int): (?)
            # 'seats':   self.internal('scheme_seats', list,),
            # Атрибуты `seats`
            # 'number' (int): Идентификатор места
            # 'seatName' (str): Название места
            # 'rowName' (str->int): Идентификатор ряда
            # 'exists' (bool): Существует место или нет (?)
            'seatCount': None,
            'image':     None,
            'descriptor': self.internal('scheme_data', list,),
        }
        scheme = self.request(method, url, data, output_mapping)

        if 'raw' in kwargs and kwargs['raw']:
            scheme['scheme_data'] = json.loads(scheme['scheme_data'])

        return scheme

    def discover_schemes(self):
        """Получение списка схем залов для записи в БД.

        Недостающая информация добавляется из мест проведения событий ``places``.

        Returns:
            list: Список словарей с информацией о схеме зала.
        """
        events = self.events()
        discovered_schemes = []

        events_by_schemes = defaultdict(list)
        for e in events:
            events_by_schemes[(e['scheme_id'])].append(e)

        for s in events_by_schemes:
            scheme = {}
            if s != 0:
                scheme_info = self.scheme(scheme_id=s)
                scheme['scheme_id'] = s
                scheme['scheme_title'] = '{place_title} ({scheme_title}) v{scheme_version}'.format(
                    place_title=events_by_schemes[s][0]['place_title'],
                    scheme_title=scheme_info['scheme_title'],
                    scheme_version=scheme_info['scheme_version']
                )
            else:
                scheme['scheme_id'] = 0
                scheme['scheme_title'] = '{place_title} (билеты без мест)'.format(
                    place_title=self.company_title
                )
            discovered_schemes.append(scheme)

        if isinstance(discovered_schemes, list) and discovered_schemes:
            discovered_schemes = sorted(discovered_schemes, key=itemgetter('scheme_id'))

        return discovered_schemes

    def groups(self):
        """Группы событий для конкретного организатора.

        Returns:
            list: Список словарей с информацией о группах событий.
        """
        method = 'GET'
        url = '/hosts/{host_id}/groups'.format(host_id=self.company_id)
        data = {
            'limit': self.limit,
        }
        output_mapping = {
            # Идентификатор группы событий
            'id':   self.internal('group_id', int,),
            # Название группы событий
            'name': self.internal('group_title', str),

            'hostId': None,
            'ticketCount': None,
        }
        groups = self.request(method, url, data, output_mapping)

        if isinstance(groups, list) and groups:
            groups = sorted(groups, key=itemgetter('group_id'))

        return groups

    def discover_groups(self):
        """Получение списка групп событий для записи в БД (с включением недостающей информации из событий).

        Returns:
            list: Список словарей с информацией о группах событий.
        """
        groups = self.groups()
        events = self.events()

        # Группировка событий по их группам
        events_by_groups = defaultdict(list)
        for e in events:
            events_by_groups[(e['group_id'])].append(e)
        # Для сохранения в БД остаются только группы, содержащие более одного события
        for i in list(events_by_groups):
            if len(events_by_groups[i]) <= 1:
                del events_by_groups[i]
        groups[:] = [g for g in groups if g.get('group_id') in events_by_groups.keys()]

        # Добавление в группу недостающей информации из самого раннего входящего в неё события
        for g in groups:
            for e in events:
                if g['group_id'] == e['group_id']:
                    g['group_datetime'] = events_by_groups[(e['group_id'])][0]['event_datetime']
                    g['group_min_price'] = events_by_groups[(e['group_id'])][0]['event_min_price']
                    g['group_text'] = events_by_groups[(e['group_id'])][0]['event_text']
                    g['scheme_id'] = (
                        events_by_groups[(e['group_id'])][0]['scheme_id'] if
                        events_by_groups[(e['group_id'])][0]['scheme_id'] else
                        0
                    )

        if isinstance(groups, list) and groups:
            groups = sorted(groups, key=itemgetter('group_datetime'))

        return groups

    def events(self, **kwargs):
        """Список событий конкретного организатора.

        Выводятся только акутальные события (продажа билетов в которых НЕ приостановлена).

        Args:
            group_id (int, optional): Идентификатор группы событий, если требуются события только в конкретной группе.

        Query parameters:
            onlyActual (bool): Только актуальные события.
            onlyWithOrderCreationAvailableViaApi (bool): Только доступные по API события (только в API версии 1).
            cityId (int): Идентификатор города.
            placeId (int): Идентификатор места проведения события.
            companyId (int): Идентификатор организатора.
            superTagId (int): Тип события (concert, perfomance, party, etc.).
            groupId  (int): Идентификатор группы событий.
            endDate (str): Конечная дата (формат ISO 8601).
            eventDateFrom (string): Работает при отсутствии параметра ``endDate`` (формат ISO 8601).
            eventDateTo (string): Работает при отсутствии параметра ``endDate`` (формат ISO 8601).
            limit (int): Лимит числа событий в ответе (по умолчанию 20).
            offset (int): С какого по счёту события начинать вывод (отброс событий в начале списка).

        Returns:
            list: Список словарей с информацией о событиях.
        """
        method = 'GET'
        url = '/events'
        data = {
            'companyId': self.company_id,
            'onlyActual': True,
            'limit': self.limit,
        }
        if self.__api_version == 1:
            data['onlyWithOrderCreationAvailableViaApi'] = True
        if 'group_id' in kwargs and kwargs['group_id']:
            data['groupId'] = kwargs['group_id']
        output_mapping = {
            # Идентификатор события
            'id':            self.internal('event_id', int,),
            # Название события
            'title':         self.internal('event_title', str,),
            # Дата и время события (в UTC) '2017-09-29T16:00:00.000+00:00'
            'beginDate':     self.internal('event_datetime', datetime,),
            # Описание события
            'description':   self.internal('event_text', str, '',),
            # Минимальная цена билета в событии
            'minPrice':      self.internal('event_min_price', Decimal,),
            # Ограничение по возрасту в событии
            'age':           self.internal('event_min_age', int, 0,),
            # Идентификатор группы
            'groupId':       self.internal('group_id', int, 0,),
            # Идентификатор зала
            'placeSchemeId': self.internal('scheme_id', int, 0,),
            # Отключены ли продажи в событии или нет
            'salesStopped':  self.internal('is_disabled', bool,),
            # Название места проведения событий
            'placeTitle':    self.internal('place_title', str,),

            'cityId': None,
            'cityName': None,
            'companyId': None,
            'companyTitle': None,
            'placeId': None,
            'placeAddress': None,
            'placeSchemeImage': None,
            'eventProviderId': None,
            'eventProviderName': None,
            'endDate': None,
            'gmtOffset': None,
            'images': None,
            'category': None,
            'currency': None,
            'maxPrice': None,
            'ticketCount': None,
            'maxTicketCountPerOrder': None,
            'soldTicketCount': None,
            'discountPercent': None,
            'superTagId': None,
            'videoUrl': None,
            'barcodeType': None  # 'Code128b       '
        }
        events = self.request(method, url, data, output_mapping)

        for e in events:
            if e['is_disabled'] is False:
                del e['is_disabled']
                e['promoter'] = ''
            else:
                del events[e]

        # Получение только актуальных событий
        return events

    def event(self, **kwargs):
        """Информация о конкретном событии.

        Args:
            event_id (int): Идентификатор события.

        Query parameters:
            onlyWithOrderCreationAvailableViaApi (bool): Только доступные по API события (только в API версии 1).
            limit (int): Лимит числа событий в ответе (по умолчанию 20).
            offset (int): С какого по счёту события начинать вывод (отброс событий в начале списка).

        Returns:
            dict: Словарь с информацией о событии.
        """
        method = 'GET'
        url = '/events/{event_id}'.format(event_id=kwargs['event_id'])
        data = None
        output_mapping = {
            # Идентификатор события
            'id':            self.internal('event_id', int,),
            # Название события
            'title':         self.internal('event_title', str,),
            # Дата и время события (в UTC) '2017-09-29T16:00:00.000+00:00'
            'beginDate':     self.internal('event_datetime', datetime,),
            # Описание события
            'description':   self.internal('event_text', str, '',),
            # Минимальная цена билета в событии
            'minPrice':      self.internal('event_min_price', Decimal,),
            # Ограничение по возрасту в событии
            'age':           self.internal('event_min_age', int, 0,),
            # Идентификатор группы
            'groupId':       self.internal('group_id', int, 0,),
            # Идентификатор зала
            'placeSchemeId': self.internal('scheme_id', int, 0,),
            # Отключены ли продажи в событии или нет
            'salesStopped':  self.internal('is_disabled', bool,),
            # Название места проведения событий
            'placeTitle':    self.internal('place_title', str,),

            'cityId': None,
            'cityName': None,
            'companyId': None,
            'companyTitle': None,
            'placeId': None,
            'placeAddress': None,
            'placeSchemeImage': None,
            'eventProviderId': None,
            'eventProviderName': None,
            'endDate': None,
            'gmtOffset': None,
            'images': None,
            'category': None,
            'currency': None,
            'maxPrice': None,
            'ticketCount': None,
            'maxTicketCountPerOrder': None,
            'soldTicketCount': None,
            'discountPercent': None,
            'superTagId': None,
            'videoUrl': None,
            'barcodeType': None  # 'Code128b       '
        }
        event = self.request(method, url, data, output_mapping)

        return event

    def discover_events(self):
        """Получение списка событий для записи в БД.

        Returns:
            list: Список словарей с информацией о событиях.
        """
        events = self.events()

        return events

    # def scheme_zones(self, **kwargs):
    #     """Список зон в конкретном зале.

    #     Args:
    #         scheme_id (int): Идентификатор зала.

    #     Returns:
    #         dict: Словарь, где ключи - идентификаторы секторов, значения - названия секторов.
    #     """
    #     scheme = self.scheme(scheme_id=kwargs['scheme_id'])

    #     scheme_zones = {s['id']: s['name'].lower() for s in scheme['scheme_zones']}

    #     return scheme_zones

    def sectors(self, **kwargs):
        """Секторы в конкретном событии (с дочерними списками мест для каждого сектора).

        Секторы в API Радарио - по сути группы билетов с одинаковой ценой (``ticket_type``).
        В разных событиях они могут содержать в себе разные места,
        т.е. секторы НЕ привязаны жёстко к местам в схеме зала.

        Args:
            event_id (int): Идентификатор события.

        Returns:
            list: Список словарей с информацией о секторах.
        """
        method = 'GET'
        url = '/events/{event_id}/ticket_types'.format(event_id=kwargs['event_id'])
        data = {
            'limit': self.limit,
        }
        if self.__api_version == 1:
            data['onlyWithOrderCreationAvailableViaApi'] = True
        output_mapping = {
            # Идентификатор группы цен
            'id':              self.internal('sector_id', int,),
            # Название группы цен
            'title':           self.internal('sector_title', str,),
            # Цена
            'price':           self.internal('price', Decimal,),
            # Группа цен с местами для сидения или нет
            'withSeats':       self.internal('is_sector_with_seats', bool,),
            # Список словарей с информацией о местах
            'seats':           self.internal('seats', list,),
            # Атрибуты seats
            # 'number' (int): Идентификатор места
            # 'seatname' (str): Название места
            # 'rowname' (str->int): Идентификатор ряда
            # 'exists' (bool): Существует место или нет (?)
            # 'isoccupied' (bool): Занято место или нет (?)
            # Общее число мест
            'ticketCount':     self.internal('seats_all_count', int,),
            # Число проданных мест
            'soldTicketCount': self.internal('seats_sold_count', int,),
            'seatBeginNumber': None,
            'seatEndNumber': None,
            'participantNameRequired': None,
            'baseTicketTypeId': None,
            'series': None,
            # Идентификатор сектора
            'zoneId': None,
        }
        sectors = self.request(method, url, data, output_mapping)
        # print('\nsectors:\n', sectors, '\n')

        for sec in sectors:
            # Число свободных мест
            sec['seats_free_count'] = sec['seats_all_count'] - sec['seats_sold_count']

        return sectors

    def seats_and_prices(self, **kwargs):
        """Доступные для продажи места в событии и список цен на билеты.

        Args:
            event_id (int): Идентификатор события.
            scheme_id (int): Идентификатор зала.

        Returns:
            list: Список словарей с информацией о доступных к заказу местах.
        """
        response = {}
        response['seats'] = {}
        response['prices'] = []

        sectors = self.sectors(event_id=kwargs['event_id'])

        if isinstance(sectors, list) and sectors:
            response['success'] = True

            prices = sorted([sec['price'] for sec in sectors])
            response['prices'] = prices
            # print('\nsectors:\n', sectors, '\n')

            for sec in sectors:
                # Билеты с местами
                if sec['seats'] is not None:
                    for s in sec['seats']:
                        # Возвращаются только существующие и ещё не проданные места
                        if s['exists'] and not s['isoccupied']:
                            seat = {}
                            # Уникальный идентификатор билета (сочетание идентификаторов сектора, ряда и места)
                            ticket_id = str(s['number'])

                            seat['sector_id'] = sec['sector_id']
                            seat['sector_title'] = sec['sector_title'].lower()
                            seat['row_id'] = int(s['rowname'])
                            seat['seat_id'] = int(s['number'])
                            seat['seat_title'] = s['seatname']
                            seat['price'] = sec['price']
                            # Порядковые номера цен на билеты для сопоставления с цветом места в схеме зала
                            seat['price_order'] = prices.index(sec['price']) + 1

                            response['seats'][ticket_id] = seat
                # Билеты без фиксированной рассадки
                else:
                    # Возвращаются все свободные билеты без фиксированной рассадки
                    for idx in range(sec['seats_free_count']):
                        seat = {}
                        # Уникальный идентификатор билета (сочетание идентификаторов сектора, ряда и места)
                        ticket_id = str(idx + 1)

                        seat['sector_id'] = sec['sector_id']
                        seat['sector_title'] = sec['sector_title'].lower()
                        seat['row_id'] = 0
                        seat['seat_id'] = idx + 1
                        seat['seat_title'] = '0'
                        seat['price'] = sec['price']
                        # Порядковые номера цен на билеты для сопоставления с цветом места в схеме зала
                        seat['price_order'] = prices.index(sec['price']) + 1

                        response['seats'][ticket_id] = seat

            del sectors
        else:
            response['success'] = False

            response['code'] = sectors['code']
            response['message'] = sectors['message']

        return response

    def reserve(self, **kwargs):
        """Добавление или удаление места в предварительном резерве мест (корзина заказа).

        Предварительный резерв, предусмотренный в API Радарио, можно НЕ использовать, т.к.:
        1) он работает только для мест С фиксированной рассадкой.
        2) предварительно зарезервироанные места НЕ исчезают из списка доступных для продажи мест.

        Поэтому этот метод в любом случае возвращает передаваемые ему атрибуты с подтверждением "успешного" результата.

        Args:
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID заказа.
            ticket_id (str): Идентификатор билета (совпадает с идентификатором места).
            action (str): Действие (`add` - добавить в резерв, `remove` - удалить из резерва).

        Returns:
            dict: Атрибуты места с подтверждением успешного или НЕуспешного резерва.
        """
        reserve = {}
        reserve['success'] = True

        reserve['event_id'] = kwargs['event_id']
        reserve['order_uuid'] = kwargs['order_uuid']
        reserve['ticket_id'] = kwargs['ticket_id']
        reserve['action'] = kwargs['action']

        return reserve

    def ticket_status(self, **kwargs):
        """Проверка состояния места (перед созданием заказа или перед онлайн-оплатой).

        В API Радарио такой функционал не предусмотрен, метод оставлен для обратной совместимости.
        Применяется для проверки предварительного резерва перед созданием заказа.

        Args:
            event_id (int): Идентификатор события.
            ticket_id (str): Идентификатор билета (совпадает с идентификатором места).

        Returns:
            dict: Информация о состоянии места.

                Содержимое результата:
                    * **success** (bool): Успешный (``True``) или НЕуспешный (``False``) результат.
                    * **status** (str): Статус места (всегда возвращается ``bypass`` для обхода проверок).
        """
        response = {}

        response['success'] = True
        response['status'] = 'bypass'

        return response

    def order_create(self, **kwargs):
        """Создание заказа из предварительно зарезервированных мест.

        Args:
            event_id (int): Идентификатор события.
            customer (dict): Информация о покупателе.

                Содержимое **customer**:
                    name (str): ФИО покупателя.
                    email (str): Электронная почта покупателя.

            tickets (dict): Словарь, содержащий словари с параметрами заказываемых билетов.

                Содержимое словарей в **tickets**:
                    ticket_uuid (uuid.UUID): Уникальный UUID билета.
                    sector_id (int): Идентификатор сектора.
                    seat_id (int): Идентификатор места.

        Returns:
            dict: Информация о созданном заказе.

            Содержимое результата:
                order_id (int): Идентификатор заказа в сервисе заказа билетов.
                tickets (dict): ловарь, содержащий словари с информацией о заказанных билетах.

                    Содержимое словарей в **tickets**:
                        ticket_uuid (uuid.UUID): Уникальный UUID билета.
                        bar_code (str): Штрих-код билета (12 символов).
        """
        method = 'POST'
        url = '/orders/reserve'
        data = {
            'eventId': kwargs['event_id'],
            'tickets': [],
            'email': kwargs['customer']['email'],
            # 'PartnerId': 'int',
            # 'Promocode': 'str',
            # 'UtmData': {
            #     'UtmSource': 'str',
            #     'UtmMedium': 'str',
            #     'UtmTerm': 'str',
            #     'UtmContent': 'str',
            #     'UtmCampaign': 'str',
            #     'UtmUserId': 'str'
            # }
        }
        for ticket_id in kwargs['tickets']:
            ticket_info = {
                'ticketTypeId': kwargs['tickets'][ticket_id]['sector_id'],
                'seatNumber': (
                    kwargs['tickets'][ticket_id]['seat_id'] if kwargs['tickets'][ticket_id]['row_id'] != 0 else None
                ),
                'participantName': kwargs['customer']['name']
            }
            data['tickets'].append(ticket_info.copy())
        output_mapping = {
            'id':      self.internal('order_id', int,),
            'tickets': self.internal('tickets', list),

            'eventId':      None,
            'orderNumber':  None,
            'ticketCount':  None,
            'amount':       None,
            'baseAmount':   None,
            'creationDate': None,
            'isPaid':       None,
        }

        order_created = self.request(method, url, data, output_mapping)

        # self.logger.info('order_created: {}'.format(order_created))
        # self.logger.info('kwargs: {}'.format(kwargs))

        # Резерв билета С фиксированной рассадкой
        # {
        #     'order_id': 2394768,
        #     'tickets': [{
        #         'userorderid': 2394768,
        #         'participantname': '-',
        #         'id': 5623032,
        #         'number': '1376802567',
        #         'barcodekey': '112853663161',
        #         'tickettypeid': 341031,
        #         'tickettypetitle': 'партер',
        #         'rowname': '7',
        #         'seatnumber': 127,
        #         'seatname': '10',
        #         'price': 1.0,
        #         'discount': 0.0,
        #         'isused': False,
        #     }]
        # }

        # Резерв билета БЕЗ фиксированной рассадки
        # {
        #     'order_id': 2394755,
        #     'tickets': [{
        #         'userorderid': 2394755,
        #         'participantname': '',
        #         'id': 5623008,
        #         'number': '2055252579',
        #         'barcodekey': '114187651661',
        #         'tickettypeid': 382752,
        #         'tickettypetitle': 'малый зал',
        #         'rowname': None,
        #         'seatnumber': None,
        #         'seatname': None,
        #         'price': 1.0,
        #         'discount': 0.0,
        #         'isused': False,
        #     }]
        # }

        response = {}
        response['tickets'] = {}

        success_condition = 'success' not in order_created or order_created['success']
        if success_condition and 'order_id' in order_created:
            response['success'] = True
            response['order_id'] = order_created['order_id']

            created_fixed_tickets = [t for t in order_created['tickets'] if t['seatnumber']]
            created_non_fixed_tickets = [t for t in order_created['tickets'] if not t['seatnumber']]

            kwargs_fixed_tickets = [t for tid, t in kwargs['tickets'].items() if t['is_fixed']]
            kwargs_non_fixed_tickets = [t for tid, t in kwargs['tickets'].items() if not t['is_fixed']]

            added_tids = set()
            added_barcodes = set()

            # Билеты С фиксированной рассадкой (штрих-коды сопоставляются по совпадению идентификатора места)
            if created_fixed_tickets:
                for cft in created_fixed_tickets:
                    for kft in kwargs_fixed_tickets:
                        if cft['seatnumber'] == kft['seat_id']:
                            ticket_id = kft['ticket_id']
                            if cft['barcodekey'] not in added_barcodes and ticket_id not in added_tids:
                                ticket = {}
                                ticket['ticket_uuid'] = kft['ticket_uuid']
                                ticket['bar_code'] = cft['barcodekey']
                                added_tids.add(ticket_id)
                                added_barcodes.add(ticket['bar_code'])
                                response['tickets'][ticket_id] = ticket.copy()
                        else:
                            continue

            # Билеты БЕЗ фиксированной рассадки (штрих-коды распределяются между всеми такими билетами)
            if created_non_fixed_tickets:
                cnft_barcodes = [t['barcodekey'] for t in created_non_fixed_tickets]

                for knft in kwargs_non_fixed_tickets:
                    ticket_id = knft['ticket_id']
                    ticket = {}
                    ticket['ticket_uuid'] = knft['ticket_uuid']
                    ticket['bar_code'] = cnft_barcodes.pop()
                    response['tickets'][ticket_id] = ticket.copy()
                    added_tids.add(ticket_id)
                    added_barcodes.add(ticket['bar_code'])

        else:
            return order_created

        # self.logger.info('response with bar_codes: {}'.format(response))

        del order_created

        return response

    def order(self, **kwargs):
        """
        Информация о конкретном заказе.

        Args:
            order_id (int): Идентификатор заказа.

        Returns:
            dict: Информация о заказе.
        """
        method = 'GET'
        url = '/orders/{order_id}'.format(order_id=kwargs['order_id'])
        data = None
        output_mapping = {
            'id':          self.internal('order_id', int,),
            'tickets':     self.internal('tickets_list', list),
            'isPaid':      self.internal('is_paid', bool),
            'ticketCount': self.internal('ticket_count', int),
            'amount':      self.internal('total', Decimal),

            'baseAmount':   None,
            'creationDate': None,
            'eventId':      None,
            'orderNumber':  None,
        }
        order = self.request(method, url, data, output_mapping)
        # print('order:', order)

        # Билеты С фиксированной рассадкой
        # {
        #     'order_id': 2508708,
        #     'is_paid': True,
        #     'tickets_list': [{
        #         'seatname': '18',
        #         'userorderid': 2508708,
        #         'rowname': '7',
        #         'discount': 0.0,
        #         'tickettypetitle': 'партер',
        #         'seatnumber': 119,
        #         'tickettypezoneid': 0,
        #         'number': '4019890878',
        #         'barcodekey': '113484653512',
        #         'id': 5896786,
        #         'price': 1.0,
        #         'participantname': '-',
        #         'tickettypeid': 2702934,
        #         'isused': False
        #     }],
        #     'ticket_count': 1,
        #     'total': Decimal('1.00')
        # }

        response = {}

        if ('success' not in order or order['success']) and 'order_id' in order:
            response['success'] = True
            response['is_paid'] = order['is_paid']
            response['tickets'] = {}

            for idx, t in enumerate(order['tickets_list']):
                ticket = {}
                ticket['bar_code'] = t['barcodekey']
                ticket['sector_id'] = t['tickettypeid']
                ticket['sector_title'] = t['tickettypetitle']
                if t['seatnumber']:
                    ticket['sector_id'] = t['tickettypeid']
                    ticket['row_id'] = int(t['rowname'])
                    ticket['seat_id'] = int(t['seatnumber'])
                    ticket['seat_title'] = t['seatname']
                else:
                    ticket['sector_id'] = 0
                    ticket['row_id'] = 0
                    ticket['seat_id'] = idx + 1
                    ticket['seat_title'] = 0
                ticket_id = str(ticket['seat_id'])
                ticket['ticket_id'] = ticket_id

                response['tickets'][ticket_id] = ticket

                response['tickets_count'] = order['ticket_count']
                response['total'] = order['total']
        else:
            response['success'] = False

            response['code'] = order['code']
            response['message'] = order['message']

        del order

        return response

    def orders(self, **kwargs):
        """Список заказов."""
        method = 'GET'
        url = '/host/orders/'
        data = None
        output_mapping = {}

        orders = self.request(method, url, data, output_mapping)
        # print('orders:', orders)

        return orders

    def order_cancel(self, **kwargs):
        """Отмена ранее созданного заказа.

        Args:
            order_id (int): Идентификатор заказа.

        Returns:
            dict: Информация об удалении заказа.

                Содержимое результата:
                    * **success** (bool): Успешный (``True``) или НЕуспешный (``False``) результат.
        """
        method = 'POST'
        url = '/orders/cancel'
        data = {
            'orderId': kwargs['order_id'],
        }
        output_mapping = {}

        cancel = self.request(method, url, data, output_mapping)
        # print('cancel:', cancel)

        # Если заказ уже был отменён ранее
        if not cancel['success'] and cancel['code'] == 2000:
            cancel['success'] = True

        return cancel

    def order_approve(self, **kwargs):
        """Отметка о подтверждении онлайн-оплаты созданного ранее заказа.

        Args:
            order_id (int): Идентификатор заказа.

        Returns:
            dict: Информация об успешной или НЕуспешной оплате.

                Содержимое результата:
                    * success (bool): Успешный (``True``) или НЕуспешный (``False``) результат.
        """
        method = 'POST'
        url = '/orders/approve'
        data = {
            'orderId': kwargs['order_id'],
        }
        output_mapping = {}

        approve = self.request(method, url, data, output_mapping)
        # print('approve:', approve)

        # Если заказ уже был отмечен как оплаченный ранее
        if not approve['success'] and approve['code'] == 2013:
            approve['success'] = True

        return approve

    def order_refund(self, **kwargs):
        """Возврат стоимости билетов (с удалением заказа и освобождением билетов для продажи).

        Args:
            order_id (int): Идентификатор заказа.
            payment_id (str): Идентификатор оплаты.
            amount (Decimal): Сумма возврата в рублях.
            reason (str): Причина возврата.

        Returns:
            dict: Информация об успешном или НЕуспешном возврате.

                Содержимое результата:
                    * success (bool): Успешный (``True``) или НЕуспешный (``False``) результат.
                    * amount (Decimal): Сумма возврата в рублях.
        """
        method = 'POST'
        url = '/orders/refund'
        data = {
            'userOrderId': kwargs['order_id'],
            'ticketNumber': None,
            'refundInitiator': 'Company',
            'comment': '',
            'reason': kwargs['reason'],
        }
        output_mapping = {
            'refundId':      self.internal('refund_id', int,),
            'refundedMoney': self.internal('amount', Decimal),
        }

        refund = self.request(method, url, data, output_mapping)
        # print('refund:', refund)

        # Если заказ уже был отмечен как возвращённый ранее
        if not refund['success'] and refund['code'] == 2000:
            refund['success'] = True

        # {
        #     'success': True
        #     'error': None,
        #     'refundId': 44347,
        #     'ticketNumbers': '№3852494138',
        #     'companyId': 1671,
        #     'tickets': [{
        #         'seatNumber': None,
        #         'seatInfo': {
        #             "rowName": "string",
        #             "colName": "string",
        #             "zoneName": "string"
        #         },
        #         'number': '3852494138',
        #         'ticketTypeId': 382752,
        #         'barcodeKey': '112264553893',
        #         'price': 1.0
        #     }],
        #     'refundMethod': 'ExternalApi',
        #     'refundType': 'Order',
        #     'refundedUserCash': 0.0,
        #     'refundedMoney': 1.0
        # }

        response = {}

        if refund['success']:
            response['success'] = True
            response['amount'] = kwargs['amount']
        else:
            response['success'] = False

            response['code'] = refund['code']
            response['message'] = refund['message']

        return response

    def promoters(self):
        """Организаторы событий для конкретного акканута Радарио.

        Returns:
            list: Список словарей с информацией о организаторах.
        """
        method = 'GET'
        url = '/company/{company_id}/event-providers'.format(company_id=self.company_id)
        data = None
        output_mapping = {
            'id':   self.internal('promoter_id', int,),
            'name': self.internal('promoter_title', str),
            'inn':         self.internal('inn', str),
            'description': self.internal('description', str),
            'commissionfeepercent': self.internal('description', Decimal),

            'companyid': None,
            'cityid': None,
            'email': None,
            'additionalemails': None,
            'phone': None,
            'allowsendsoldticketreportforprevday': None,
            'allowsendsoldticketreportforalltime': None,
            'creationddate': None,
            'updatedate': None,
            'deleted': None,
            'address': None,
            'contractnumber': None,
            'contractdate': None,
        }
        promoters = self.request(method, url, data, output_mapping)

        if isinstance(promoters, list) and promoters:
            promoters = sorted(promoters, key=itemgetter('promoter_id'))

        return promoters

    # GET /categories - Get categories

    # GET /cities - Get cities

    # GET /hosts/{id} - Get company by id

    # GET /places/{place_id} - Get event place by id

    # GET /events/{event_id}/tickets - Get tickets (only bought or booked) by event_id
    # * limit     int
    # * offset    int

    # GET /events/{event_id}/orders - Get orders by event_id
    # * limit     int
    # * offset    int

    # GET /event-providers/{event_provider_id} - Get event provider by id

    # GET /company/{company_id}/event-providers - Get event providers by company id

    # POST /orders/update
    # {
    #   "orderId": "int",
    #   "email": "str"
    # }

    # GET /tickets/{ticket_id}/pdf - Get ticket in pdf format

    # POST /orders/send - Send order to customer's email
    # {
    #   "orderId": "int"
    # }

    # GET /host/orders/{order_id} - Get order complex info by id.
    # Get only orders that created for host current account belongs to.

    # GET /host/orders - Get current account host orders complex info.

    # GET /promocodes - Get Promocodes
    # * code         str        required     Promocode code
    # * companyId    integer    required     Company id
