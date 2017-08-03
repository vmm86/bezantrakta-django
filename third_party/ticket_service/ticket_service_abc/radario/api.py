import requests
from datetime import datetime
from decimal import Decimal
from operator import itemgetter

from ..abc import TicketService
from .shortcuts import prettify_json_response


class Radario(TicketService):
    """
    Класс для работы с API Радарио.

    Документация: https://radario.github.io/slate/radario.api/

    The only one accepted Content-Type is `application/json`.
    Messages charset is set to UTF-8.

    Attributes:
        api_version
        api_base_url
        limit
        offset
        time_to_live
    """
    slug = 'radario'

    def __init__(self, init):
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
        """Общий конструктор запросов к API.

        Args:
            method (str): HTTP-метод в верхнем регистре (GET, POST).
            url (str): Относительный URL конкретного метода API.
            data (dict): Query-параметры для GET или тело запроса для POST.
            output_mapping (dict): Словарь для замены.
            test (bool, optional): Тестируется ли работа метода (при тестировании постобработка не происходит).

        Returns:
            list, dict: Обработанный ответ конкретного метода API.
        """
        url_path = self.api_base_url + url
        print('request url: ', url_path)

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

        # print('response: ', response.json())

        if response.status_code == 200:
            # Если тестируем работу метода - получаем JSON-ответ без обработки
            if test:
                return response.json()
            else:
                return prettify_json_response(response.json(), output_mapping)
        else:
            return {'code': response.status_code, 'message': 'response error', }

    def version(self):
        """Версия API Радарио.

        Returns:
            str: Версия API Радарио.
        """
        return self.api_version

    def places(self):
        """Места проведения событий в конкретном городе.

        Returns:
            list: Список словарей с информацией о местах проведения событий.
        """
        method = 'GET'
        url = '/places'
        data = {
            'cityId': self.city_id,
            'onlyWithOrderCreationAvailableViaApi': True,
            'limit': self.limit,
        }
        output_mapping = {
            'address':   None,
            'cityId':    None,
            'cityName':  None,
            'id':        ('place_id', int,),
            'latitude':  None,
            'longitude': None,
            'title':     ('place_title', str,),
        }
        return self.request(method, url, data, output_mapping)

    def venue(self, **kwargs):
        """
        Залы (схемы залов) в местах проведения событий.

        Args:
            **kwargs: Параметры.

        Returns:
            dict: Словарь с информацией о зале, в том числе о секторах (зонах) и их местах.
        """
        method = 'GET'
        url = '/schemes/{scheme_id}'.format(scheme_id=kwargs['venue_id'])
        # Возможность получения schema raw descriptor
        if 'raw' in kwargs and kwargs['raw']:
            url += '/raw'
        data = None
        output_mapping = {
            'id': ('venue_id', int,),
            'name': ('venue_title', str,),
            'seatCount': None,
            'zones': ('venue_zones', list,),
            'image': None,
            'version': ('venue_version', int,)
        }
        return self.request(method, url, data, output_mapping)

    def discover_venues(self):
        """
        Получение списка залов для записи в БД.
        Отдельными залами в API Радарио фактически является сущность `scheme`.
        Сущность `place` - отдельные здания, не связанные напрямую со схемами залов.

        Returns:
            list: Список словарей с информацией о зале.
        """
        from collections import defaultdict

        events = self.events()
        schemes = []

        events_by_schemes = defaultdict(list)
        for e in events:
            events_by_schemes[(e['venue_id'])].append(e)

        for v in events_by_schemes:
            scheme = {}
            if v != 0:
                scheme_info = self.venue(venue_id=v)
                scheme['venue_id'] = v
                scheme['venue_title'] = '{place_title} ({venue_title}) v{venue_version}'.format(
                    place_title=events_by_schemes[v][0]['place_title'],
                    venue_title=scheme_info['venue_title'],
                    venue_version=scheme_info['venue_version']
                )
            else:
                scheme['venue_id'] = 0
                scheme['venue_title'] = '{place_title} (билеты без мест)'.format(
                    place_title=self.company_title
                )
            schemes.append(scheme)

        return schemes

    def sectors(self, **kwargs):
        """
        Секторы в конкретном событии.

        Args:
            **kwargs: Параметры.

        Returns:
            dict: Словарь, где ключи - идентификаторы сектров, значения - названия секторов.
        """
        venue = self.venue(venue_id=kwargs['venue_id'])

        return {v['id']: v['name'].lower() for v in venue['venue_zones']}

    def groups(self):
        """
        Список групп.

        Returns:
            list: Список словарей с информацией о группах.
        """
        method = 'GET'
        url = '/hosts/{host_id}/groups'.format(host_id=self.company_id)
        data = {
            'limit': self.limit,
        }
        output_mapping = {
            'hostId': None,
            'id': ('group_id', int,),
            'name': ('group_title', str),
            'ticketCount': None,
        }
        return self.request(method, url, data, output_mapping)

    def discover_groups(self):
        """
        Получение списка событий с включением недостающей информации из групп событий для записи в БД.

        Returns:
            list: Список словарей с информацией о группах.
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
                    g['venue_id'] = (
                        events_by_groups[(e['group_id'])][0]['venue_id'] if
                        events_by_groups[(e['group_id'])][0]['venue_id'] is not None else
                        0
                    )

        # Сортировка групп по дате/времени
        groups = sorted(groups, key=itemgetter('group_datetime'))

        return groups

    def events(self, **kwargs):
        """
        Список событий для конкретного организатора.

        Args:
            group_id (int, optional): Идентификатор группы событий.

        Query params:
            onlyActual (bool)
            cityId (int)
            placeId (int)
            companyId (int)
            superTagId (int)    Event type id (e.g concert, perfomance, party, etc.)
            groupId  (int)    event group id
            endDate (str)    ISO 8601 format.
            onlyWithOrderCreationAvailableViaApi (bool)    Return events with permission to create.
            limit (int)    (default 20)
            offset (int)

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
            'age': ('event_min_age', int, 0,),
            'beginDate': ('event_datetime', datetime,),  # '2017-09-29T16:00:00.000+00:00'
            'category': None,
            'cityId': None,
            'cityName': None,
            'companyId': None,
            'companyTitle': None,
            'currency': None,
            'description': ('event_text', str, '',),
            'discountPercent': None,
            'endDate': None,
            'eventProviderId': None,
            'eventProviderName': None,
            'gmtOffset': None,
            'groupId': ('group_id', int, 0,),
            'id': ('event_id', int,),
            'images': None,
            'maxPrice': None,
            'maxTicketCountPerOrder': None,
            'minPrice': ('event_min_price', Decimal,),
            'placeAddress': None,
            'placeId': ('place_id', int,),
            'placeSchemeId': ('venue_id', int, 0,),
            'placeSchemeImage': None,
            'placeTitle': ('place_title', str,),
            'salesStopped': ('is_disabled', bool,),
            'superTagId': None,
            'ticketCount': None,
            'title': ('event_title', str,),
            'videoUrl': None,
        }
        events = self.request(method, url, data, output_mapping)

        # Получение только актуальных событий
        return [e for e in events if e['is_disabled'] is False]

    def discover_events(self):
        """
        Получение списка актуальных событий для записи в БД.
        Отфильтровываются только те события, продажа билетов в которых НЕ приостановлена.

        Returns:
            list: Список словарей с информацией о событиях.
        """
        return self.events()

    def event(self, **kwargs):
        """
        Информация о конкретном событии.

        * onlyWithOrderCreationAvailableViaApi    bool    Return events with permission to create.
        * limit         int    (default 20)
        * offset        int

        Args:
            **kwargs: Параметры.

        Returns:
            dict: Словарь с информацией о событии.
        """
        method = 'GET'
        url = '/events/{event_id}'.format(event_id=kwargs['event_id'])
        data = None
        output_mapping = {
            'age': ('event_min_age', int,),
            'beginDate': ('event_datetime', datetime,),  # '2017-09-29T16:00:00.000+00:00'
            'category': None,
            'cityId': None,
            'cityName': ('city_title', str,),
            'companyId': None,
            'companyTitle': None,
            'currency': None,
            'description': ('event_text', str,),
            'discountPercent': None,
            'endDate': None,
            'eventProviderId': None,
            'eventProviderName': None,
            'gmtOffset': None,
            'groupId': ('group_id', int,),
            'id': ('event_id', int,),
            'images': None,
            'maxPrice': None,
            'maxTicketCountPerOrder': None,
            'minPrice': ('event_min_price', Decimal,),
            'placeAddress': None,
            'placeId': ('place_id', int,),
            'placeSchemeId': ('venue_id', int,),
            'placeSchemeImage': None,
            'placeTitle': ('place_title', int,),
            'salesStopped': ('is_disabled', bool),
            'superTagId': None,  # Event type id (concert, perfomance, party, etc.)
            'ticketCount': ('ticket_count', int,),
            'title': ('title', str,),
            'videoUrl': None,
        }
        event = self.request(method, url, data, output_mapping)

        event['event_text'] = event['event_text'] if event['event_text'] is not None else ''

        return event

    def price_groups(self, **kwargs):
        """
        Группы цен в конкретном событии с дочерними списками мест для каждой группы цен.

        Args:
            **kwargs: Description

        Returns:
            TYPE: Description
        """
        method = 'GET'
        url = '/events/{event_id}/ticket_types'.format(event_id=kwargs['event_id'])
        data = {
            'onlyWithOrderCreationAvailableViaApi': True,
            'limit': self.limit,
        }
        output_mapping = {
            'id': ('price_group_id', int,),
            'title': ('price_group_title', str,),
            'price': ('price', Decimal,),
            'baseTicketTypeId': None,
            'seats': ('seats', list,),
            'seatBeginNumber': None,
            'seatEndNumber': None,
            'soldTicketCount': ('seats_sold_count', int,),
            'ticketCount': ('seats_all_count', int,),
            'withSeats': ('is_price_group_with_seats', bool,),
            'series': None,
            'zoneId': None,
        }
        price_groups = self.request(method, url, data, output_mapping)

        for pg in price_groups:
            pg['seats_free_count'] = pg['seats_all_count'] - pg['seats_sold_count']

        return price_groups

    def prices(self, **kwargs):
        """
        Список цен на билеты по возрастанию для легенды схемы зала.
        """
        price_groups = self.price_groups(event_id=kwargs['event_id'])

        prices = sorted([pg['price'] for pg in price_groups])

        return prices

    def seats(self, **kwargs):
        """
        Доступные для продажи места в конкретном событии.
        """
        price_groups = self.price_groups(event_id=kwargs['event_id'])
        seats = []
        prices = sorted([pg['price'] for pg in price_groups])

        venues = self.venue(venue_id=kwargs['venue_id'])
        sectors = {v['name'].lower(): v['id'] for v in venues['venue_zones']}
        # print(sectors)

        for pg in price_groups:
            for s in pg['seats']:
                # Возвращаются только существующие и ещё не проданные места
                if s['exists'] and not s['isOccupied']:
                    # del s['exists']
                    # del s['isOccupied']
                    s['sector_id'] = sectors[pg['price_group_title']]
                    # Названия секторов
                    s['sector_title'] = pg['price_group_title'].lower()
                    s['row_id'] = int(s.pop('rowName'))
                    s['seat_id'] = int(s.pop('number'))
                    s['seat_title'] = int(s.pop('seatName'))
                    s['price_group_id'] = pg['price_group_id']
                    s['price'] = pg['price']
                    # Порядковые номера цен на билеты для сопоставления с цветом места в схеме зала
                    s['price_order'] = prices.index(pg['price']) + 1
                    seats.append(s)

        seats = sorted(seats, key=itemgetter('price', 'sector_id', 'row_id', 'seat_id'))

        return seats

    def reserve(self, **kwargs):
        """
        Добавление или удаление места в предварительном резерве мест (корзина заказа).
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

    def order_create(self, **kwargs):
        """
        Создание резерва мест и заказа.

        Args:
            event_id (int): Идентификатор события.
            customer (dict): Информация о покупателе.
            tickets (list): Информация о заказываемых билетах.

        Returns:
            TYPE: Description
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
        output_mapping = {}
        return self.request(method, url, data, output_mapping, test=True)

    def order_delete(self, **kwargs):
        """
        Удаление резерва мест и заказа.
        """
        method = 'POST'
        url = '/orders/cancel'
        data = {
            'orderId': kwargs['order_id'],
        }
        output_mapping = {}
        return self.request(method, url, data, output_mapping, test=True)

    def order_payment(self, **kwargs):
        """
        Оплата созданного ранее заказа.
        tickets - список из словарей.
        """
        method = 'POST'
        url = '/orders/approve'
        data = {
            'orderId': kwargs['order_id'],
        }
        output_mapping = {}
        return self.request(method, url, data, output_mapping, test=True)

    def order_refund(self, **kwargs):
        """
        Возврат билетов (с удалением заказа и освобождением билетов для продажи).

        Args:
            order_id: int Уникальный номер заказа.
            reason:   str Причина возврата.
            comment:  str Комментарий (опционально).
        """
        method = 'POST'
        url = '/orders/refund'
        data = {
            # 'Method': 7,
            'UserOrderId': kwargs['order_id'],
            'TicketNumber': None,
            'RefundInitiator': 'company',
            'Comment': kwargs['comment'],
            'Reason': kwargs['reason'],
        }
        output_mapping = {}
        return self.request(method, url, data, output_mapping, test=True)

    def order(self, **kwargs):
        """
        Информация о конкретном заказе.
        """
        method = 'GET'
        url = '/orders/{order_id}'.format(order_id=kwargs['order_id'])
        data = None
        output_mapping = {}
        return self.request(method, url, data, output_mapping, test=True)

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
