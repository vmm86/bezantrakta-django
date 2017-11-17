import dateutil.parser
import requests
from datetime import datetime
from decimal import Decimal
from operator import itemgetter

from ..abc import TicketService


class Radario(TicketService):
    """Класс для работы с API Радарио.

    Любой метод, делающий запросы к API, вызывает для этого конструктор запросов ``request``.

    `Документация по API Радарио <https://radario.github.io/slate/radario.api/>`_.

    The only one accepted Content-Type is ``application/json``.
    Messages charset is set to UTF-8.

    Атрибуты класса:
        **slug** (str): Псевдоним для инстанцирования класса (``radario``).

    Attributes:
        api_version
        api_base_url
        limit
        offset
        time_to_live
    """
    slug = 'radario'

    def __init__(self, init):
        """Конструктор класса.

        Args:
            init (dict): Словарь с параметрами для инстанцирования класса.
        """
        super().__init__()

        # Параметры подключения
        self.__api_id = init['api_id']
        self.__api_key = init['api_key']
        self.city_id = init['city_id']
        self.company_id = init['company_id']
        self.company_title = init['company_title']
        self.api_version = 'v1'
        self.api_base_url = 'https://api.radario.ru/{version}'.format(version=self.api_version)

        # Параметры вывода
        self.limit = 100
        self.offset = 0
        self.time_to_live = 15

    def __str__(self):
        return '{cls}(city: {city}, company: {company_title})'.format(
            cls=self.__class__.__name__,
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
        url_path = self.api_base_url + url
        # print('request url: ', url_path)

        headers = {
            'api-id':  self.__api_id,
            'api-key': self.__api_key,
        }

        if method == 'GET':
            response = requests.get(url_path, params=data, headers=headers)
        elif method == 'POST':
            response = requests.post(url_path, json=data, headers=headers)
        else:
            pass

        print('response: ', response.json(), '\n')

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
        response_success = True if response['success'] else False
        response_code = response['error']['errorCode'] if not response_success else 0
        response_message = response['error']['message'] if not response_success else 'OK'

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
                    return {'success': True, 'code': 0, 'message': 'OK', }
                else:
                    return {'success': False, 'code': response_code, 'message': response_message, }

            # Если в ответе - множество записей
            if type(iterable) is list:
                # Конвертация ключей в человекопонятные значения
                for d in iterable:
                    self.humanize_with_type_casting(d, output_mapping)
                    d['success'] = True
            # Если в ответе - одна запись
            elif type(iterable) is dict:
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
                        if internal.type is str and type(iterable[internal.key]) is not str:
                            iterable[internal.key] = str(internal.default_value)
                            # Если получена пустая строка - поиск значения по умолчанию
                            iterable[internal.key] == (
                                internal.default_value if
                                iterable[internal.key] == '' and internal.default_value is not None else
                                iterable[internal.key]
                            )
                        elif internal.type is int and type(iterable[internal.key]) is not int:
                            iterable[internal.key] = int(iterable[internal.key])
                        elif internal.type is bool and type(iterable[internal.key]) is not bool:
                            iterable[internal.key] = True if iterable[internal.key] in self.BOOLEAN_VALUES else False
                        elif internal.type is Decimal and type(iterable[internal.key]) is not Decimal:
                            iterable[internal.key] = self.decimal_price(iterable[internal.key])
                        elif internal.type is datetime and type(iterable[internal.key]) is not datetime:
                            # '2017-09-29T16:00:00.000+00:00'
                            iterable[internal.key] = dateutil.parser.parse(iterable[internal.key])
                        # Приведение ключей списка из словарей к нижнему регистру
                        elif internal.type is list and type(iterable[internal.key][0]) is dict:
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
        return self.api_version

    def places(self):
        """Места проведения событий (в конкретном городе).

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GET'
        url = '/places'
        data = {
            'cityId': self.city_id,
            'onlyWithOrderCreationAvailableViaApi': True,
            'limit': self.limit,
        }
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

        places = sorted(places, key=itemgetter('place_id'))

        return places

    def scheme(self, **kwargs):
        """Информация о схеме зала в месте проведения событий.

        Ответ в том числе содержит информацию о секторах (зонах) и их местах.

        Args:
            scheme_id (int): Идентификатор схемы зала.
            raw (bool, optional): Опциональная возможность получения schema raw descriptor.

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
            # Атрибуты zones
            # 'colcount' (int): (?)
            # 'id' (int): Идентификатор сектора
            # 'name' (str): Название сектора
            # 'withseats' (bool): Сектор с местами для сидения или нет
            # 'rowcount' (int): (?)
            # 'seats':   self.internal('scheme_seats', list,),
            # Атрибуты seats
            # 'number' (int): Идентификатор места
            # 'seatname' (str): Название места
            # 'rowname' (str->int): Идентификатор ряда
            # 'exists' (bool): Существует место или нет (?)
            'seatCount': None,
            'image':     None,
        }
        scheme = self.request(method, url, data, output_mapping)

        return scheme

    def discover_schemes(self):
        """Получение списка залов для записи в БД.

        Отдельными схемами залами в API Радарио является сущность ``scheme``.
        Сущность ``place`` - места событий как отдельные здания (не связанные напрямую со схемами залов).

        Returns:
            list: Список словарей с информацией о зале.
        """
        from collections import defaultdict

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

        groups = sorted(groups, key=itemgetter('group_id'))

        return groups

    def discover_groups(self):
        """Получение списка групп событий для записи в БД (с включением недостающей информации из событий).

        Returns:
            list: Список словарей с информацией о группах событий.
        """
        from collections import defaultdict

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
                        events_by_groups[(e['group_id'])][0]['scheme_id'] is not None else
                        0
                    )

        # Сортировка групп по дате/времени
        groups = sorted(groups, key=itemgetter('group_datetime'))

        return groups

    def events(self, **kwargs):
        """Список событий конкретного организатора.

        Выводятся только те события, продажа билетов в которых НЕ приостановлена.

        Args:
            group_id (int, optional): Идентификатор группы событий, если требуются события в конкретной группе.

        Query parameters:
            onlyActual (bool): Вывод только актуальных событий.
            cityId (int): Идентификатор города.
            placeId (int): Идентификатор места проведения события.
            companyId (int): Идентификатор организатора.
            superTagId (int): Тип события (e.g concert, perfomance, party, etc.).
            groupId  (int): Идентификатор группы событий.
            endDate (str): Конечная дата (ISO 8601).
            onlyWithOrderCreationAvailableViaApi (bool): Только события, доступные для запроса по API.
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
            'onlyWithOrderCreationAvailableViaApi': True,
            'limit': self.limit,
        }
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
            # Название места проведения событий
            'placeTitle':    self.internal('place_title', str,),
            # Идентификатор зала
            'placeSchemeId': self.internal('scheme_id', int, 0,),
            # Отключены ли продажи в событии или нет
            'salesStopped':  self.internal('is_disabled', bool,),

            'category': None,
            'cityId': None,
            'cityName': None,
            'companyId': None,
            'companyTitle': None,
            'currency': None,
            'discountPercent': None,
            'endDate': None,
            'eventProviderId': None,
            'eventProviderName': None,
            'gmtOffset': None,
            'images': None,
            'maxPrice': None,
            'maxTicketCountPerOrder': None,
            'placeId': None,
            'placeAddress': None,
            'placeSchemeImage': None,
            'superTagId': None,
            'ticketCount': None,
            'videoUrl': None,
        }
        events = self.request(method, url, data, output_mapping)

        for e in events:
            if e['is_disabled'] is False:
                del e['is_disabled']
            else:
                del events[e]

        # Получение только актуальных событий
        return events

    def event(self, **kwargs):
        """Информация о конкретном событии.

        Args:
            event_id (int): Идентификатор события.

        Query parameters:
            onlyWithOrderCreationAvailableViaApi
            limit
            offset

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

            'category': None,
            'cityId': None,
            'cityName': None,
            'companyId': None,
            'companyTitle': None,
            'currency': None,
            'discountPercent': None,
            'endDate': None,
            'eventProviderId': None,
            'eventProviderName': None,
            'gmtOffset': None,
            'images': None,
            'maxPrice': None,
            'maxTicketCountPerOrder': None,
            'placeId': None,
            'placeAddress': None,
            'placeSchemeImage': None,
            'placeTitle': None,
            'superTagId': None,
            'ticketCount': None,
            'videoUrl': None,
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

    def sectors(self, **kwargs):
        """Список секторов в конкретном зале.

        Args:
            scheme_id (int): Идентификатор зала.

        Returns:
            dict: Словарь, где ключи - идентификаторы секторов, значения - названия секторов.
        """
        scheme = self.scheme(scheme_id=kwargs['scheme_id'])

        return {s['id']: s['name'].lower() for s in scheme['scheme_zones']}

    def price_groups(self, **kwargs):
        """Группы цен в конкретном событии (с дочерними списками мест для каждой группы цен).

        Args:
            event_id (int): Идентификатор события.

        Returns:
            list: Список словарей с информацией о группах цен.
        """
        method = 'GET'
        url = '/events/{event_id}/ticket_types'.format(event_id=kwargs['event_id'])
        data = {
            'onlyWithOrderCreationAvailableViaApi': True,
            'limit': self.limit,
        }
        output_mapping = {
            # Идентификатор группы цен
            'id':              self.internal('price_group_id', int,),
            # Название группы цен
            'title':           self.internal('price_group_title', str,),
            # Цена
            'price':           self.internal('price', Decimal,),
            # Группа цен с местами для сидения или нет
            'withSeats':       self.internal('is_price_group_with_seats', bool,),
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
            'baseTicketTypeId': None,
            'seatBeginNumber': None,
            'seatEndNumber': None,
            'series': None,
            'zoneId': None,
        }
        price_groups = self.request(method, url, data, output_mapping)

        for pg in price_groups:
            # Число свободных мест
            pg['seats_free_count'] = pg['seats_all_count'] - pg['seats_sold_count']

        return price_groups

    def prices(self, **kwargs):
        """Список цен на билеты по возрастанию для легенды схемы зала.

        Args:
            event_id (int): Идентификатор события.

        Returns:
            list: Список цен по возрастанию.
        """
        price_groups = self.price_groups(event_id=kwargs['event_id'])

        prices = sorted([pg['price'] for pg in price_groups])

        return prices

    def seats(self, **kwargs):
        """Доступные для продажи места в конкретном событии.

        Args:
            event_id (int): Идентификатор события.
            scheme_id (int): Идентификатор зала.

        Returns:
            list: Список словарей с информацией о доступных к заказу местах.
        """
        response = {}

        price_groups = self.price_groups(event_id=kwargs['event_id'])
        print('price_groups: ', price_groups, '\n')
        seats = []
        prices = sorted([pg['price'] for pg in price_groups])
        response['prices'] = prices

        scheme = self.scheme(scheme_id=kwargs['scheme_id'])
        print('scheme: ', scheme, '\n')
        if kwargs['scheme_id'] != 0:
            sectors = {s['name'].lower(): s['id'] for s in scheme['scheme_zones']}
        else:
            sectors = {pg['price_group_title'].lower(): pg['price_group_id'] for pg in price_groups}
        print('sectors: ', sectors, '\n')

        for pg in price_groups:
            # Билеты с местами
            if pg['seats'] is not None:
                for s in pg['seats']:
                    # Возвращаются только существующие и ещё не проданные места
                    if s['exists'] and not s['isoccupied']:
                        s['sector_id'] = sectors[pg['price_group_title']]
                        # Названия секторов
                        s['sector_title'] = pg['price_group_title'].lower()
                        s['row_id'] = int(s.pop('rowname'))
                        s['seat_id'] = int(s.pop('number'))
                        s['seat_title'] = s.pop('seatname')
                        s['price_group_id'] = pg['price_group_id']
                        s['price'] = pg['price']
                        # Порядковые номера цен на билеты для сопоставления с цветом места в схеме зала
                        s['price_order'] = prices.index(pg['price']) + 1
                        del s['exists']
                        del s['isoccupied']
                        seats.append(s)
            # Билеты без мест
            else:
                # Возвращаются все свободные билеты без мест
                for s in range(pg['seats_free_count']):
                    seat = {}
                    seat['sector_id'] = sectors[pg['price_group_title']]
                    # Названия секторов
                    seat['sector_title'] = pg['price_group_title'].lower()
                    seat['row_id'] = 0
                    seat['seat_id'] = 0
                    seat['seat_title'] = ''
                    seat['price_group_id'] = pg['price_group_id']
                    seat['price'] = pg['price']
                    # Порядковые номера цен на билеты для сопоставления с цветом места в схеме зала
                    seat['price_order'] = prices.index(pg['price']) + 1
                    seats.append(seat)

        seats = sorted(seats, key=itemgetter('price', 'sector_id', 'row_id', 'seat_id'))
        response['seats'] = seats

        return response

    def reserve(self, **kwargs):
        """Добавление или удаление места в предварительном резерве мест (корзина заказа).

        Можно не использовать для резерва метод API Радарио и хранить резерв в cookie.
        Метод будет возвращать обратно передаваемые ему атрибуты места с подтверждением успешного/НЕуспешного резерва.

        Args:
            action (str): Действие (`add` - добавить в резерв, `remove` - удалить из резерва).
            event_id (int): Идентификатор события.
            price_group_id (int): Идентификатор группы цен.
            seat_id (int): Идентификатор места.

        Returns:
            dict: Атрибуты места с подтверждением успешного или НЕуспешного резерва.
        """
        # method = 'POST'
        # data = {
        #     'EventId': kwargs['event_id'],
        #     'TicketTypeId': kwargs['price_group_id'],
        #     'SeatNumber': kwargs['seat_id'],
        # }
        # if kwargs['action'] == 'add':
        #     url = '/orders/add_pre_reserved_seat'
        #     # Таймаут предварительного резерва в минутах (по умолчанию - 15 минут)
        #     data['TimeToLive'] = self.time_to_live
        # elif kwargs['action'] == 'remove':
        #     url = '/orders/remove_pre_reserved_seat'
        # output_mapping = {}
        # return self.request(method, url, data, output_mapping)

        reserve = {}
        reserve['success'] = True
        for kw in kwargs:
            reserve[kw] = kwargs[kw]
        return reserve

    def ticket_status(self, **kwargs):
        """Проверка состояния места (перед созданием заказа или перед онлайн-оплатой).

        В API Радарио такой функционал не предусмотрен, метод оставлен для обратной совместимости.
        Применяется для проверки предварительного резерва перед созданием заказа.

        Args:
            event_id (int): Идентификатор события.
            ticket_uuid (str): Уникальный UUID билета.
            sector_id (int): Идентификатор сектора.
            row_id (int): Идентификатор ряда.
            seat_id (int): Идентификатор места.

        Returns:
            dict: Информация о состоянии места.
                order_id (int): Идентификатор заказа, если он был создан, иначе None.
                ticket_uuid (str): Уникальный UUID билета.
                seat_status (str): Статус места.
        """
        response = {}

        response['order_id'] = None
        response['ticket_uuid'] = kwargs['ticket_uuid']
        response['seat_status'] = 'reserved'

        return response

    def order_create(self, **kwargs):
        """Создание заказа из предварительно зарезервированных мест.

        Args:
            event_id (int): Идентификатор события.
            customer (dict): Информация о покупателе.
            customer[name] (str): ФИО покупателя.
            customer[email] (str): Электронная почта покупателя.
            tickets (list): Информация о зарезервированных билетах.
            tickets[seat_id] (int): Идентификатор места.
            tickets[price_group_id] (int): Идентификатор группы цен.

        Returns:
            dict: Информация о созданном заказе.
            order_id (int): Идентификатор заказа в сервисе заказа билетов.
            tickets (list): Информация о заказанных билетах.
            tickets[ticket_uuid] (str): Уникальный UUID билета (на данный момент генерируется на клиенте).
            tickets[bar_code] (str): Штрих-код билета (12 символов).
        """
        method = 'POST'
        url = '/orders/reserve'
        data = {
            'EventId': kwargs['event_id'],
            'Tickets': [],
            'Email': kwargs['customer']['email'],
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
        for t in kwargs['tickets']:
            ticket_info = {
                'TicketTypeId': t['price_group_id'],
                'SeatNumber': t['seat_id'],
                'ParticipantName': kwargs['customer']['name']
            }
            data['Tickets'].append(ticket_info.copy())
        output_mapping = {
            'success': self.internal('success', bool,),
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

        order = self.request(method, url, data, output_mapping)
        print('order: ', order)

        response = {}
        response['tickets'] = []

        if order['success']:
            response['order_id'] = order['order_id']

            for o in order['tickets']:
                ticket = {}
                for t in kwargs['tickets']:
                    ticket['ticket_uuid'] = (
                        t['ticket_uuid'] if
                        (o['seatnumber'] == t['seat_id'] and
                         o['tickettypeid'] == t['price_group_id']) else
                        None
                    )
                ticket['bar_code'] = o['barcodekey']  # 12 символов
                # o['participantName'] == '-' ???
                response['tickets'].append(ticket.copy())
        else:
            return order

        return response

    def order(self, **kwargs):
        """
        Информация о конкретном заказе.

        Args:
            order_id (int): Идентификатор заказа.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GET'
        url = '/orders/{order_id}'.format(order_id=kwargs['order_id'])
        data = None
        output_mapping = {}
        return self.request(method, url, data, output_mapping)

    def order_delete(self, **kwargs):
        """Удаление заказа.

        Args:
            order_id (int): Идентификатор заказа.

        Returns:
            dict: Информация об удалении заказа.
                success (bool): Успешное или НЕуспешное удаление заказа.
        """
        method = 'POST'
        url = '/orders/cancel'
        data = {
            'orderId': kwargs['order_id'],
        }
        output_mapping = {}

        delete = self.request(method, url, data, output_mapping)

        return delete

    def order_payment(self, **kwargs):
        """Отметка об оплате созданного ранее заказа.

        Args:
            order_id (int): Идентификатор заказа.

        Returns:
            dict: Информация об успешной или НЕуспешной оплате.
        """
        method = 'POST'
        url = '/orders/approve'
        data = {
            'orderId': kwargs['order_id'],
        }
        output_mapping = {}

        payment = self.request(method, url, data, output_mapping)

        return payment

    def order_refund(self, **kwargs):
        """Возврат стоимости билетов (с удалением заказа и освобождением билетов для продажи).

        Args:
            order_id (int): Идентификатор заказа.
            reason (str): Причина возврата.

        Returns:
            dict: Информация об успешном или НЕуспешном возврате.
        """
        method = 'POST'
        url = '/orders/refund'
        data = {
            # 'Method': 7,
            'UserOrderId': kwargs['order_id'],
            'TicketNumber': None,  # ???
            'RefundInitiator': 'Company',
            'Comment': '',
            'Reason': kwargs['reason'],
        }
        output_mapping = {}

        refund = self.request(method, url, data, output_mapping)

        return refund

    # def categories(self):
    #     """Список категорий событий."""
    #     method = 'GET'
    #     url = '/categories'
    #     data = {
    #         'companyId': self.company_id,
    #         'onlyWithOrderCreationAvailableViaApi': True,
    #         'limit': self.limit,
    #     }
    #     output_mapping = {
    #         'id':   ('category_id', int,),
    #         'name': ('category_title', str,),
    #     }
    #     return self.request(method, url, data, output_mapping)

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
