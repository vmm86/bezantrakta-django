import xmltodict
import xml
import zeep
from datetime import datetime
from operator import itemgetter

from decimal import Decimal

from ..abc import TicketService
from .shortcuts import prettify_xml_response


class SuperBilet(TicketService):
    """
    Класс для работы с API СуперБилет.
    Любой метод, делающий запросы к API, возвращает вызов конструктора запросов request.

    Class attributes:
        slug (str): Псевдоним для инстанцирования класса (`superbilet`).

    Attributes:
        client (TYPE): Description
        slug (str): Description
    """
    slug = 'superbilet'

    def __init__(self, init):
        """Конструктор класса.

        Args:
            init (dict): Словарь с параметрами для инстанцирования класса.
        """
        super().__init__()

        # Параметры подключения
        self.__host = init['host']
        self.__user = init['user']
        self.__pswd = init['pswd']
        self.__mode = init['mode']

        # Экземпляр SOAP-клиента
        self.client = zeep.Client(wsdl=self.__host)

    def __str__(self):
        return '{cls}({host}: {mode})'.format(
            cls=self.__class__.__name__,
            host=self.__host.split('/')[4],
            mode=self.__mode,
        )

    def request(self, method, input_mapping, data, output_mapping, test=False):
        """
        Конструктор запросов к API СуперБилет.
        Даже если в ответе всего одна запись, она в люом случае кладётся в список.

        Args:
            method (str): HTTP-метод (GET или POST).
            input_mapping (dict): Сопоставление входных человекоНЕпонятных параметров входным человекопонятным.
            data (dict): Необходимые для конкретного метода параметры.
            output_mapping (dict): Сопоставление выходных человекоНЕпонятных параметров выходным человекопонятным.
            test (bool, optional): Опциональный параметр для тестирования работы.

        Returns:
            list: Ответ запрошенного метода СуперБилет
        """
        # Тело запроса по умолчанию
        default_params = {
            'GateReq': {
                'ReqLogin': {
                    'UserName': self.__user,
                    'UserPass': self.__pswd,
                },
                'ReqBody': {
                    'InputRow': [],
                }
            }
        }

        # Добавление необходимых параметров к телу запроса, если запрос непустой
        if data is None:
            pass
        else:
            # Если в запросе - много записей
            if type(data) is list:
                for d in data:
                    params = {}
                    for external, internal in input_mapping.items():
                        try:
                            params['@' + external] = d[internal]
                        except KeyError:
                            pass
                    default_params['GateReq']['ReqBody']['InputRow'].append(params.copy())
            # Если в запросе - одна запись
            elif type(data) is dict:
                params = {}
                for external, internal in input_mapping.items():
                    try:
                        params['@' + external] = data[internal]
                    except KeyError:
                        pass
                default_params['GateReq']['ReqBody']['InputRow'].append(params.copy())

        # Формирование тела запроса
        if method == 'GetVersion':
            data = {}
        elif method == 'CheckSoldTickets':
            data = {
                'Login': self.__user,
                'Password': self.__pswd,
                'Value': xmltodict.unparse(default_params, pretty=True),
            }
        else:
            data = {
                'Value': xmltodict.unparse(default_params, pretty=True),
            }

        # print('METHOD:\n', method, '\n')
        # print('DATA:\n', data['Value'], '\n')

        result = self.client.service[method](**data)

        # print('XML:\n', result, '\n')

        # Если тестируем работу метода - получаем XML-ответ без обработки
        if test:
            return result
        else:
            # Если получаем ответ не в XML - выводим его без обработки
            try:
                pretty_result = prettify_xml_response(result, output_mapping)
                # Если в ответе одна запись - в любом случае кладём её в список
                if type(pretty_result) is dict:
                    pretty_result_container = []
                    pretty_result_container.append(pretty_result)
                    return pretty_result_container
                else:
                    return pretty_result
            except xml.parsers.expat.ExpatError:
                return result

    def version(self):
        """
        Версия СуперБилет.

        Returns:
            str: Версия СуперБилет.
        """
        method = 'GetVersion'
        input_mapping = None
        data = None
        output_mapping = None
        return self.request(method, input_mapping, data, output_mapping)

    def places(self):
        """
        Места проведения событий.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GetLocationList'
        input_mapping = None
        data = None
        output_mapping = {
            'address_t':   None,
            'city':        None,
            'cod_t':       ('place_id', int,),
            'name_t':      ('place_title', str,),
            'result_code': ('result_code', int,),
            'tel_t':       None,
        }
        return self.request(method, input_mapping, data, output_mapping)

    def venues(self, **kwargs):
        """
        Залы в местах проведения событий.

        Args:
            place_id (int): Идентификатор места проведения событий.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GetHallList'
        input_mapping = {
            'cod_t': 'place_id',
        }
        data = kwargs
        output_mapping = {
            'address_h':   None,
            'cod_th':      ('venue_id', int,),
            'name_h':      ('venue_title', str,),
            'name_h2':     None,
            'result_code': ('result_code', int,),
            'tel_h':       None,
        }
        return self.request(method, input_mapping, data, output_mapping)

    def discover_venues(self):
        """
        Получение списка залов с включением недостающей информации из мест проведения событий для записи в БД.

        Returns:
            list: Список словарей с информацией о зале.
        """
        discovered_venues = []
        places = self.places()
        for p in places:
            venues = self.venues(place_id=p['place_id'])
            for v in venues:
                v['venue_title'] = '{place_title} ({venue_title})'.format(
                    place_title=p['place_title'],
                    venue_title=v['venue_title'].lower()
                )
                del v['result_code']
                discovered_venues.append(v)

        return discovered_venues

    def groups(self):
        """
        Группы событий ("шоу").
        В СуперБилет каждое событие находится в своей группе событий, даже если это событие в одном экземпляре.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GetShowList'
        input_mapping = None
        data = None
        output_mapping = {
            'actors':      None,
            'annotation':  ('group_text', str,),
            'author':      None,
            'cod_ganr':    None,
            'cod_categ':   None,
            'cod_show':    ('group_id', int,),
            'duration':    None,
            'name_show':   ('group_title', str,),
            'name_show2':  None,
            'name_ganr':   None,
            'name_categ':  None,
            'note1':       None,
            'note2':       None,
            'note3':       None,
            'producer':    None,
            'result_code': ('result_code', int,),
            # СуперБилет Театр
            'autor':            None,
            'ispremiere':       None,
            'withintermission': None,
        }
        return self.request(method, input_mapping, data, output_mapping)

    def discover_groups(self):
        """
        Получение списка событий с включением недостающей информации из групп событий для записи в БД.

        Returns:
            list: Список словарей с информацией о событиях.
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
                    g['venue_id'] = events_by_groups[(e['group_id'])][0]['venue_id']

        # Сортировка групп по дате/времени
        groups = sorted(groups, key=itemgetter('group_datetime'))

        return groups

    def events(self, **kwargs):
        """
        События.

        Args:
            place_id (int): Идентификатор места проведения событий.
            venue_id (int): Идентификатор зала.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GetEventList'
        input_mapping = {
            'cod_t':  'place_id',
            'cod_th': 'venue_id',
        }
        data = kwargs
        output_mapping = {
            'actors':           None,
            'annotation':       ('event_text', str,),
            'author':           None,
            'cod_ganr':         None,
            'cod_cate':         None,
            'cod_show':         ('group_id', int,),
            'cod_t':            ('place_id', int,),
            'cod_h':            ('venue_id', int,),
            'eventdate':        ('event_date', str,),  # '24.10.2017'
            'eventduration':    None,
            'eventnote':        None,
            'eventtime':        ('event_time', str,),  # '19:00:00'
            'is_primera':       None,
            'maxprice':         ('event_max_price', Decimal,),
            'maxpricesell':     None,
            'maxpricediscount': None,
            'minprice':         ('event_min_price', Decimal,),
            'minpricesell':     None,
            'minpricediscount': None,
            'name_ganr':        None,
            'name_categ':       None,
            'name_show':        ('event_title', str,),
            'nombilkn':         ('event_id', int,),
            'note1':            None,
            'note2':            None,
            'note3':            None,
            'note4':            None,
            'producer':         None,
            'result_code':      ('result_code', int,),
            # СуперБилет Театр
            'num_web': None,
            'num_boxoffice': None,
        }
        events = self.request(method, input_mapping, data, output_mapping)

        for e in events:
            # Преобразование даты/времени
            date, month, year = e['event_date'].split('.')
            event_datetime = '{year}-{month}-{date} {time}'.format(
                year=year,
                month=month,
                date=date,
                time=e['event_time']
            )
            e['event_datetime'] = datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S')
            del e['event_date']
            del e['event_time']

            del e['place_id']

            try:
                e['event_text'] is None
            except KeyError:
                e['event_text'] = ''

            try:
                e['event_min_price'] is None
            except KeyError:
                e['event_min_price'] = Decimal(0).quantize(Decimal('1.00'))

        # Сортировка событий по дате/времени
        events = sorted(events, key=itemgetter('event_datetime'))

        return events

    def discover_events(self):
        """
        Получение списка событий с включением недостающей информации из групп событий для записи в БД.

        Returns:
            list: Список словарей с информацией о событиях.
        """
        return self.events()

    def sectors(self, **kwargs):
        """
        Секторы в конкретном событии.
        """
        method = 'GetSectorList'
        input_mapping = {
            'NomBilKn': 'event_id',
        }
        data = kwargs
        output_mapping = {
            'cod_sec':     ('sector_id', int,),
            'name_sec':    ('sector_title', str,),
            'nombilkn':    None,
            'placescount': ('seats_all_count', int,),  # только в СуперБилет Агентство
            'result_code': ('result_code', int,),
        }
        sectors = self.request(method, input_mapping, data, output_mapping)

        return {s['sector_id']: s['sector_title'].lower() for s in sectors}

    def seats(self, **kwargs):
        """
        Доступные для продажи места в конкретном событии.

        Args:
            event_id (int): Идентификатор события.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GetEvailPlaceList'
        input_mapping = {
            'NomBilKn': 'event_id',
        }
        data = kwargs
        output_mapping = {
            'cod_sec':       ('sector_id', int,),
            'nombilkn':      None,
            'price':         ('price', Decimal,),
            'pricesell':     None,
            'pricediscount': None,
            'result_code':   ('result_code', int,),
            'row':           ('row_id', int,),
            'seat':          ('seat_id', int,),
            # СуперБилет Театр
            'cod_hs':        None,  # Объект на схеме зала из метода `scheme`
        }
        sectors = self.sectors(event_id=kwargs['event_id'])
        seats = self.request(method, input_mapping, data, output_mapping)

        from collections import defaultdict

        # Группировка мест по ценам билетов
        seats_by_prices = defaultdict(list)
        for s in seats:
            seats_by_prices[(s['price'])].append(s)

        prices = sorted([p for p in seats_by_prices])

        for s in seats:
            # Названия секторов
            s['sector_title'] = sectors[s['sector_id']].lower()
            s['seat_title'] = s['seat_id']
            # Порядковые номера цен на билеты для сопоставления с цветом места в схеме зала
            s['price_order'] = prices.index(s['price']) + 1
            del s['result_code']

        seats = sorted(seats, key=itemgetter('price', 'sector_id', 'row_id', 'seat_id'))

        return seats

    def sector_seats(self, **kwargs):
        """
        Доступные места в конкретном секторе в конкретном событии.

        Args:
            event_id (int): Идентификатор события.
            sector_id (int): Идентификатор сектора.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GetPlaceForSector'
        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
        }
        data = kwargs
        output_mapping = {
            'cod_hs':        None,  # Объект на схеме зала из метода `scheme`
            'cod_sec':       ('sector_id', int,),
            'name_sector':   None,
            'nombilkn':      None,
            'price':         ('price', Decimal,),
            'pricesell':     None,
            'pricediscount': None,
            'result_code':   ('result_code', int,),
            'row':           ('row_id', int,),
            'seat':          ('seat_id', int,),
        }
        return self.request(method, input_mapping, data, output_mapping)

    def prices(self, **kwargs):
        """
        Список цен на билеты по возрастанию для легенды схемы зала.

        Args:
            event_id (int): Идентификатор события.

        Returns:
            method: Вызов конструктора запросов request.
        """
        from collections import defaultdict

        seats = self.seats(event_id=kwargs['event_id'])

        # Группировка мест по ценам билетов
        seats_by_prices = defaultdict(list)
        for s in seats:
            seats_by_prices[(s['price'])].append(s)

        # Сортировка цен
        prices = sorted([p for p in seats_by_prices])

        return prices

    def reserve(self, **kwargs):
        """
        Добавление или удаление места в предварительном резерве мест (корзина заказа).

        Args:
            event_id (int): Идентификатор события.
            sector_id (int): Идентификатор события.
            row_id (int): Идентификатор события.
            seat_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID как номер сессии (любая строка до 50 однобайтовых символов).

        Returns:
            method: Вызов конструктора запросов request.
        """
        if kwargs['action'] == 'add':
            method = 'PreSetReservation'
        elif kwargs['action'] == 'remove':
            method = 'FreePreReservation'
        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'row':      'row_id',
            'seat':     'seat_id',
            'session':  'order_uuid',
        }
        data = kwargs
        output_mapping = {
            'cod_sec':       ('sector_id', int,),
            'nombilkn':      None,
            'price':         ('price', Decimal,),
            'pricesell':     None,
            'pricediscount': None,
            'result_code':   ('result_code', int,),
            'row':           ('row_id', int,),
            'seat':          ('seat_id', int,),
            'session':       ('order_uuid', str,),
        }
        reserve = self.request(method, input_mapping, data, output_mapping)

        response = {}
        response['action'] = kwargs['action']

        try:
            response['success'] = True if reserve[0]['result_code'] == 0 else False
        except KeyError:
            response['success'] = False
            response['code'] = reserve[0]['code']
            response['message'] = reserve[0]['message']

        return response

    def order_create(self, tickets):
        """
        Создание резерва мест и заказа.
        Агентство вызывает обычный метод, а Театр вызывает Ext-метод с одними и теми же аргументами.
        tickets - список из словарей.

        Args:
            tickets (TYPE): Description

        Returns:
            method: Вызов конструктора запросов request.
        """
        if self.__mode == 'agency':
            method = 'SetReservation'
        elif self.__mode == 'theatre':
            method = 'SetReservationExt'
        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'row':      'row_id',
            'seat':     'seat_id',
            'Session':  'session_id',

            'NameSpektator':  'name',
            'TelSpektator':   'phone',
            'EmailSpektator': 'email',
            'Delivery':       'is_delivery',
            'Address':        'delivery_address',
        }
        data = tickets
        output_mapping = {
            'session':       ('session_id', str,),
            'cod_sec':       ('sector_id', int,),
            'nombilkn':      None,
            'reservid':      ('order_id', str,),
            'reservdate':    None,
            'result_code':   ('result_code', int,),
            'price':         ('price', Decimal,),
            'pricesell':     None,
            'pricediscount': None,
            'row':           ('row_id', int,),
            'seat':          ('seat_id', int,),
            'orderbarcode':  ('bar_code', str,),  # Агентство
            'barcode':       ('bar_code', str,),  # Театр

            'idspectator':    ('customer_id', str,),
            'namespektator':  ('name', str,),
            'telspektator':   ('phone', str,),
            'emailspektator': ('email', str,),

            'delivery': ('is_delivery', bool,),
            'address':  ('delivery_address', str,),
            'metro':    None,
            'notes':    None,
            'orderid':  None,  # ID доставки ???
        }
        return self.request(method, input_mapping, data, output_mapping)

    def order_delete(self, tickets):
        """
        Удаление резерва мест и заказа.
        tickets - список из словарей.
        """
        method = 'FreeReservation'
        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'row':      'row_id',
            'seat':     'seat_id',
            'session':  'session_id',
            'reservID': 'order_id',
        }
        data = tickets
        output_mapping = {
            'session':     ('session_id', str,),
            'cod_sec':     ('sector_id', int,),
            'nombilkn':    None,
            'reservid':    ('order_id', str,),
            'reservdate':  None,
            'result_code': ('result_code', int,),
            'price':       ('price', Decimal,),
            'row':         ('row_id', int,),
            'seat':        ('seat_id', int,),
        }
        return self.request(method, input_mapping, data, output_mapping)

    def order_check(self, **kwargs):
        """
        Проверка состояния билетов в заказе, в том числе перед онлайн-оплатой.
        В новой версии не работает корректно, если передано несколько мест для проверки состояния.
        """
        method = 'GetCurrentState'
        input_mapping = {
            'DateFrom': 'from_date',
            'DateTo':   'to_date',
            'TimeFrom': 'from_time',
            'TimeTo':   'to_time',

            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'Row':      'row_id',
            'Seat':     'seat_id',
        }
        data = kwargs
        output_mapping = {
            'actiondate':     ('date', str,),
            'actiontime':     ('time', str,),
            'gateactiondate': None,
            'gateactiontime': None,
            'gatestatus':     None,
            'gatereservid':   None,
            'gateuser':       None,  # bool установлен ли последний статус текущим пользователем шлюза
            'nombilkn':       ('event_id', int,),
            'cod_sec':        ('sector_id', int,),
            'row':            ('row_id', int,),
            'seat':           ('seat_id', int,),
            'price':          ('price', Decimal,),
            'pricesell':      None,
            'pricediscount':  None,
            'paymentdate':    None,
            'transactionid':  ('transaction_id', str,),
            'status':         ('seat_status', str,),  # "" - свободен, SOL - продан, RES - забронирован
            'reservid':       ('order_id', str,),
            'session':        ('session_id', str,),
            'idspectator':    ('customer_id', int,),  # ???
            'result_code':    ('result_code', int,),
        }
        return self.request(method, input_mapping, data, output_mapping)

    def order_pre_payment_check(self, tickets):
        """
        Проверка заказа перед оплатой.
        tickets - список из словарей.
        """
        method = 'CheckSoldTickets'
        input_mapping = {
            'NomBilKn':      'event_id',
            'cod_sec':       'sector_id',
            'row':           'row_id',
            'seat':          'seat_id',
            'session':       'session_id',
            'reservID':      'order_id',

            'TransactionID': 'transaction_id',
            'PaymentDate':   'payment_date',
            'PaymentTime':   'payment_time',

            'Login':         'login',
            'Password':      'password',
        }
        data = tickets
        output_mapping = {
            'session':     ('session_id', str,),
            'cod_sec':     ('sector_id', int,),
            'nombilkn':    None,
            'row':         ('row_id', int,),
            'seat':        ('seat_id', int,),
            'reservid':    ('order_id', str,),
            'price':       ('price', Decimal,),
            'result_code': ('result_code', int,),
        }
        return self.request(method, input_mapping, data, output_mapping)

    def order_payment(self, tickets):
        """
        Оплата созданного ранее заказа (простая или расширенная).
        Агентство вызывает обычный метод, а Театр вызывает Ext-метод с одними и теми же аргументами.
        tickets - список из словарей.
        """
        if self.__mode == 'agency':
            method = 'SetSold'
        elif self.__mode == 'theatre':
            method = 'SetSoldExt'
        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'row':      'row_id',
            'seat':     'seat_id',
            'session':  'session_id',

            'TransactionID': 'transaction_id',
            'PaymentDate':   'payment_date',
            'PaymentTime':   'payment_time',
        }
        data = tickets
        output_mapping = {
            'nombilkn':      None,
            'cod_sec':       ('sector_id', int,),
            'row':           ('row_id', int,),
            'seat':          ('seat_id', int,),
            'price':         ('price', Decimal,),   # в случае ошибки = 0
            'pricesell':      None,
            'pricediscount':  None,
            'session':       ('session_id', str,),

            'reservid':      ('order_id', str,),    # в случае ошибки = 0
            'reservdate':    ('order_date', str,),  # в случае ошибки = ""
            'transactionid': ('transaction_id', str,),
            'paymentdate':   ('payment_date', str,),
            'paymenttime':   ('payment_time', str,),

            'result_code':   ('result_code', int,),
        }
        return self.request(method, input_mapping, data, output_mapping)

# SetSoldTickets(Login, Password, Value) -> return: xsd:string

# Отличия в параметрах нового метода SetSoldTickets от старого метода SetSoldExt:
# 1. Логин и пароль в новых методах передается отдельными параметрами вызова, а не внутри входного xml
# 2. Параметр session переименован в sessionID
# 3. Новый обязательный входной параметр ReservID
# 4. Новый обязательный входной параметр price

    def scheme(self, **kwargs):
        """
        Схема зала для события/сектора.
        """
        method = 'GetSchemaHallList'
        input_mapping = {
            'NomBilKn': 'event_id',
        }
        data = kwargs
        output_mapping = {
            'cod_hs': ('object_id', int,),
            'nombilkn': None,
            'objectid': ('object_type_id', int,),  # 0 - кресло, 1 - точка линии, 2 - метка
            'objectname': ('object_type_title', str,),  # Place - кресло, Point - точка линии, Label - метка
            'placesize': ('scheme_size', int,),  # 22 или 15
            'width': ('object_width', int,),  # Ширина кресла (0 для остальных объектов)
            'height': ('object_height', int,),  # Высота кресла (0 для остальных объектов)
            'pointindex': ('point_index', int,),  # Индекс точки в пределах одной линии
            'grouppointindex': ('group_point_index', int,),  # Индекс линии в пределах зала
            'cx': ('object_x', int,),  # Координата объекта по оси X
            'cy': ('object_y', int,),  # Координата объекта по оси Y
            'angel': ('object_angle', int,),  # Угол поворота кресла (0 для остальных объектов)
            'row': ('row_id', int,),  # Ряд
            'seat': ('seat_id', int,),  # Место
            'cod_sec': ('sector_id', int,),  # ID сектора
            'name_sec': ('sector_title', str,),  # Наименование сектора
            'label': ('object_label', str,),  # Текст метки
            'backcolor': ('object_background', str,),  # Цвет фона метки (FFFFFF для прозрачного фона)
            'fontcolor': ('object_color', str,),  # Цвет шрифта метки или цвет линии
            'fontsize': ('object_font_size', int,),  # Размер шрифта метки
            'imageindex': ('object_image_index', int,),  # Индекс картинки метки
            'minx': ('object_min_x', int,),  # Минимальная координата зала по оси X
            'miny': ('object_min_y', int,),  # Минимальная координата зала по оси Y
            'maxx': ('object_max_x', int,),  # Максимальная координата зала по оси X
            'maxy': ('object_max_y', int,),  # Максимальная координата зала по оси Y
        }
        return self.request(method, input_mapping, data, output_mapping)

    def log(self, **kwargs):
        """
        Журнал операций СуперБилета (обычный или расширенный).
        """
        input_mapping = {
            'DateFrom': 'from_date',
            'DateTo':   'to_date',
            'TimeFrom': 'from_time',
            'TimeTo':   'to_time',
        }
        ext = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'Row':      'row_id',
            'Seat':     'seat_id',
        }
        for external, internal in ext.items():
            if internal in kwargs.keys():
                method = 'GetLogExt'
            else:
                method = 'GetLog'
        input_mapping.update(ext)
        data = kwargs
        output_mapping = {
            'actiondate':     ('date', str,),
            'actiontime':     ('time', str,),
            'actiondone':     ('operation', str,),
            'nombilkn':       ('event_id', int,),
            'cod_sec':        ('sector_id', int,),
            'row':            ('row_id', int,),
            'seat':           ('seat_id', int,),
            'price':          ('price', Decimal,),
            'pricesell':      None,
            'pricediscount':  None,
            'reservid':       ('order_id', str,),
            'reservdate':     ('order_date', str,),  # 30.12.1899 00:00

            'session':        ('session_id', str,),
            'idspectator':    ('customer_id', str,),  # ???
            'namespectator':  ('name', str,),
            'telspectator':   ('phone', str,),
            'emailspectator': ('email', str,),

            'result_code':    ('result_code', int,),
        }
        return self.request(method, input_mapping, data, output_mapping)

    # SoldGift(Login, Password, SoldGiftRequest: ns0:TSoldGiftRequest) -> return: ns0:TSoldGiftAnswer
    # RefundOrder(Value) -> return: xsd:string (только в СуперБилет Агентство)

    # ViewEventsForPasses(Login, Password) -> return: ns0:TViewEventsForPassesAnswer
    # ViewPlacesWithBarcodeList(Login, Password, ViewPlacesWithBarcodeListRequest) -> return: ns0:TViewPlacesWithBarcodeListAnswer

    # GetCategoriesList
    # GetShowCategoriesList
    # GetDeliveriesList ???
    # GetOfficesList ???

    # GetStat(Login: xsd:string, Password: xsd:string, TonlineAdminPassword: xsd:string, Request: ns0:TStatRequest) -> return: ns0:TStatAnswer

    # TestServer(Request: ns0:TTestServerRequest) -> return: ns0:TTestServerAnswer
    # TestServerLoopback(Request: ns0:TTestServerRequest) -> return: ns0:TTestServerRequest
