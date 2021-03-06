import dateutil.parser
import logging
import requests
import uuid
import xml
import xmltodict

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from operator import itemgetter

from zeep import Client, CachingClient, xsd
from zeep.cache import SqliteCache
from zeep.exceptions import Error
from zeep.transports import Transport

try:
    from project.shortcuts import BOOLEAN_VALUES
except ImportError:
    BOOLEAN_VALUES = ('True', 'true', 1, '1', 'y', 'yes', 'д', 'да',)

from ..abc import TicketService


class SuperBilet(TicketService):
    """Класс для работы с API СуперБилет.

    Любой метод, делающий запросы к API, вызывает для этого конструктор запросов ``request``.

    Каждая запись в ответе имеет атрибут ``result_code``.
    При успешном ответе он равен ``0``, при НЕуспешном ответе содержит код ошибки (int) и сообщение об ошибке (str).

    Атрибуты класса:
        slug (str): Псевдоним для инстанцирования класса (``superbilet``).
        logger (logging.Logger): Объект для логирования информации о работе класса.
        bar_code_length (int): Длина штрих-кода.
        request_timeout (int): Время в секундах, при превышении которого долгие запросы логируются в ``logger``.
        LOG_OPERATIONS (dict): Коды ошибок и сообщения об ошибках.
        RESPONSE_CODES (dict): Значения параметра ``actiondone`` в методе ``GetLog``.
        SEAT_STATUSES (dict): Статусы места в предварительном резерве, созданном или оплаченном заказе.

    Instance attributes:
        client (zeep.Client|zeep.CachingClient): Экземпляр SOAP-клиента.
    """
    slug = 'superbilet'
    logger = logging.getLogger('ticket_service.superbilet')
    bar_code_length = 20
    request_timeout = 5

    LOG_OPERATIONS = {
        'PlacePreRes':          'Предварительный резерв: при добавлении не найдено место',
        'PreRes':               'Предварительный резерв: добавлено',
        'ErrorPreRes':          'Предварительный резерв: при добавлении произошла ошибка (откат транзакции)',
        'FailPreRes':           'Предварительный резерв: место не добавлено',
        'NoSessionFreePreRes':  'Предварительный резерв: при удалении не найден order_uuid',
        'NoPlaceFreePreRes':    'Предварительный резерв: при удалении не найдено место',
        'FailFreePreRes':       'Предварительный резерв: при удалении произошла ошибка',
        'ErrorFreePreRes':      'Предварительный резерв: при удалении произошла ошибка',
        'FreePreRes':           'Предварительный резерв: удалено',

        'NoSessionSetRes':      'Создание заказа: не найден order_uuid',
        'NoPlaceSetRes':        'Создание заказа: не найдено место',
        'FailSetRes':           'Создание заказа: ошибка (не найден предварительный резерв или order_uuid)',
        'ErrorSetRes':          'Создание заказа: ошибка',
        'SetRes':               'Создание заказа: успешно',
        'NoSessionFreeRes':     'Удаление заказа: не найден order_uuid',
        'NoPlaceFreeRes':       'Удаление заказа: не найдено место',
        'FailFreeRes':          'Удаление заказа: ошибка (не найден предварительный резерв или order_uuid)',
        'ErrorFreeRes':         'Удаление заказа: ошибка',
        'NoReservationFreeRes': 'Удаление заказа: нет предварительного резерва для места',
        'FreeRes':              'Удаление заказа: успешно',

        'NoSessionSetSold':     'Оплата заказа: не найден order_uuid',
        'NoReservationSetSold': 'Оплата заказа: не найден предварительный резерв',
        'NoPlaceSetSold':       'Оплата заказа: не найдено место',
        'ErrorSetSold':         'Оплата заказа: ошибка',
        'FailSetSold':          'Оплата заказа: ошибка (не найден предварительный резерв или order_uuid)',
        'SetSold':              'Оплата заказа: успешно',
    }

    RESPONSE_CODES = {
        # Общие коды ответа
        0:  'Успешный результат',
        1:  'Место занято/отсутствует или событие неактивно (прошло, отменено, продажа не разрешена)',
        2:  'Ошибка интерфейса - неверный формат данных',
        3:  'Ошибка доступа к базе данных',
        4:  'Неверный номер сессии или удалён предварительный резерв',
        5:  'Ошибка авторизации',
        6:  'Системная ошибка в работе шлюза',
        7:  'Отсутствует шлюз для подключения (версия V2) или отсутствует покупатель',
        # Только в "Супербилет-Театр"
        8:  'Не заполнены Ф.И.О. покупателя',
        9:  'Не заполнены контактные данные покупателя (телефон или email)',
        10: 'Не указана транзакция в методе SetSoldExt',
        11: 'Не указана дата транзакции в методе SetSoldExt',
        12: 'Не указано время транзакции в методе SetSoldExt',
        13: 'Заказ оплачен - место не подлежит удалению',
        # Только в "Супербилет-Театр" версии 6.2.P+
        14: 'Пользователь не является пользователем шлюза',
        15: 'Пользователю запрещен доступ к шлюзу',
    }

    SEAT_STATUSES = {
        'FREE': 'free',      # свободен ''
        'SEL':  'reserved',  # предварительный резерв
        'RES':  'ordered',   # созданный заказ
        'SOL':  'approved',  # оплаченный заказ
        'OTH':  '?',         # ?
    }

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

        wsdl_cache = '/tmp/{}.db'.format(SuperBilet.slug)
        # Таймаут в секундах (30 дней) на повторный запрос WSDL
        timeout = 60 * 60 * 24 * 30
        self.__cache = SqliteCache(path=wsdl_cache, timeout=timeout)
        self.__transport = Transport(cache=self.__cache)

        # Экземпляр SOAP-клиента (обработка возможных исключений в грёбаном СуперГовне)
        init_dt_start = datetime.now()
        try:
            self.client = Client(self.__host, transport=self.__transport)
        except requests.exceptions.RequestException as exc:
            self.logger.error('__init__ exception: {}'.format(repr(exc)))

        init_dt_end = datetime.now()
        init_dt_delta = (init_dt_end - init_dt_start).total_seconds()
        # Логирование слишком длительных запросов
        if init_dt_delta > SuperBilet.request_timeout:
            self.logger.error('__init__ is too long: {} s.'.format(init_dt_delta))

    def __str__(self):
        return '{cls}({host}: {mode})'.format(
            cls=self.__class__.__name__,
            host=self.__host.split('/')[4],
            mode=self.__mode,
        )

    def request(self, method, input_mapping, data, output_mapping, test=False):
        """Конструктор запросов к API СуперБилет.

        Даже если в ответе всего одна запись, она в любом случае кладётся в список.

        Args:
            method (str): HTTP-метод (``GET`` или ``POST``).
            input_mapping (dict): Сопоставление входных человекоНЕпонятных параметров входным человекопонятным.
            data (list|dict): Необходимые для конкретного метода параметры.
            output_mapping (dict): Сопоставление выходных человекоНЕпонятных параметров выходным человекопонятным.
            test (bool, optional): Опциональный параметр для тестирования работы.

        Returns:
            list: Ответ запрошенного метода СуперБилет.
        """
        # print('\nSuperBilet request:', method, data, '\n')

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
        if data is not None:
            # Если в запросе - много записей
            if isinstance(data, list):
                for d in data:
                    params = {}
                    for external, internal in input_mapping.items():
                        if internal in d:
                            params['@' + external] = d[internal]
                    default_params['GateReq']['ReqBody']['InputRow'].append(params.copy())
            # Если в запросе - одна запись
            elif isinstance(data, dict):
                params = {}
                for external, internal in input_mapping.items():
                    if internal in data:
                        params['@' + external] = data[internal]
                default_params['GateReq']['ReqBody']['InputRow'].append(params.copy())

        # print('METHOD: ', method, '\n')

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
            # print('DATA:\n', data['Value'], '\n')

        request_dt_start = datetime.now()
        # Обработка возможных исключений в грёбаном СуперГовне
        try:
            response = self.client.service[method](**data)
        except Error as exc:
            self.logger.error('request exception: {}'.format(repr(exc)))

            response = {}
            response['success'] = False
            response['message'] = repr(exc)

            return response
        request_dt_end = datetime.now()
        request_dt_delta = (request_dt_end - request_dt_start).total_seconds()
        # Логирование слишком длительных запросов
        if request_dt_delta > SuperBilet.request_timeout:
            self.logger.error('{method} request is too long: {seconds} s.'.format(
                method=method,
                seconds=request_dt_delta)
            )

        # print('XML:\n', response, '\n')

        # Если тестируем работу метода - получаем XML-ответ без обработки
        if test:
            return response
        else:
            # Если получаем ответ не в XML - выводим его без обработки
            try:
                pretty_response = self.prettify_response(response, output_mapping)
                # Если ответ успешный, но в нём только одна запись - она кладётся в список
                # Затем по типу ответа (список или словарь) можно понимать, успешный он или НЕуспешный
                if isinstance(pretty_response, dict) and 'error' not in pretty_response:
                    pretty_response_container = []
                    pretty_response_container.append(pretty_response)
                    return pretty_response_container
                else:
                    return pretty_response
            except xml.parsers.expat.ExpatError:
                return response

    def prettify_response(self, response, output_mapping):
        """Конвертация XML-ответа в структуру данных Python и последующая обработка.

        Args:
            response (dict): Ответ конкретного метода API.
            output_mapping (dict): Словарь для замены.

        Returns:
            list: Обработанный ответ конкретного метода API.
        """
        response = xmltodict.parse(response, dict_constructor=dict, attr_prefix='@', cdata_key='#text')
        response_code = int(response['GateAnswer']['AnswerResult']['ResultCode'])
        response_count = int(response['GateAnswer']['AnswerResult']['RecordCount'])
        try:
            response_message = response['GateAnswer']['AnswerResult']['ResultText']
        except KeyError:
            response_message = ''

        # Если ответ успешен
        if response_code == 0:
            # Тело ответа с необходимыми данными, если они есть
            if response_count > 0:
                iterable = response['GateAnswer']['AnswerBody']['Row']

                # Если в ответе - множество записей
                if isinstance(iterable, list):
                    # Ключи в нижнем регистре
                    iterable = [{k.lower(): v for k, v in d.items()} for d in iterable]
                    # print('iterable before: ', iterable, '\n')
                    # Конвертация ключей в человекопонятные значения и приведение типов
                    for d in iterable:
                        self.humanize_with_type_casting(d, output_mapping)
                        # Если ответ пришёл с ошибкой
                        if 'result_code' in d and d['result_code'] != 0:
                            d['message'] = self.RESPONSE_CODES[d['result_code']]
                # Если в ответе - одна запись
                elif isinstance(iterable, dict):
                    # Ключи в нижнем регистре
                    iterable = {k.lower(): v for k, v in iterable.items()}
                    # Конвертация ключей в человекопонятные значения и приведение типов
                    self.humanize_with_type_casting(iterable, output_mapping)
                    # Если ответ пришёл с ошибкой
                    if iterable['result_code'] != 0:
                        code = iterable['result_code']
                        message = self.RESPONSE_CODES[code]
                        return {'error': True, 'code': code, 'message': message, }
                return iterable
            else:
                return {'error': True, 'code': response_code, 'message': 'По вашему запросу ничего не найдено', }
        # Если ответ НЕуспешен
        else:
            return {'error': True, 'code': response_code, 'message': response_message, }

    def humanize_with_type_casting(self, iterable, output_mapping):
        """Конвертация ключей в человекопонятные значения и приведение типов данных.

        Args:
            iterable (dict): Ответ метода.
            output_mapping (dict): Словарь для замены.
        """
        for external, internal in output_mapping.items():
            external_key = '@' + external
            if external_key in iterable:
                # НЕнужные на выходе записи удаляются из ответа
                if internal is None:
                    iterable.pop(external_key)
                # Нужные на выходе записи пересохраняются в требуемые ключи из output_mapping
                else:
                    iterable[internal.key] = iterable.pop(external_key)
                    # print('internal: ', internal)
                    # print('value: ', type(iterable[internal.key]), iterable[internal.key])

                    # Если получено пустое значение - поиск значения по умолчанию
                    if iterable[internal.key] in ('', None):
                        if internal.default_value is not None:
                            iterable[internal.key] = internal.default_value
                    # Если получено НЕпустое значение - приведение типов данных
                    else:
                        if internal.type is str and not isinstance(iterable[internal.key], str):
                            # Если получена пустая строка - поиск значения по умолчанию
                            iterable[internal.key] == (
                                internal.default_value if
                                iterable[internal.key] == '' and internal.default_value is not None else
                                iterable[internal.key]
                            )
                        elif internal.type is int and not isinstance(iterable[internal.key], int):
                            iterable[internal.key] = (
                                0 if
                                iterable[internal.key] == '' else
                                int(iterable[internal.key])
                            )
                        elif internal.type is bool and not isinstance(iterable[internal.key], bool):
                            iterable[internal.key] = True if iterable[internal.key] in BOOLEAN_VALUES else False
                        elif internal.type is Decimal and not isinstance(iterable[internal.key], Decimal):
                            iterable[internal.key] = self.decimal_price(iterable[internal.key])
                        elif internal.type is datetime and not isinstance(iterable[internal.key], datetime):
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

            #             print('value: ', type(iterable[internal.key]), iterable[internal.key], '\n')
            # print('\n')

    def version(self):
        """Версия API СуперБилет.

        Returns:
            str: Версия API СуперБилет.
        """
        method = 'GetVersion'
        input_mapping = None
        data = None
        output_mapping = None
        return self.request(method, input_mapping, data, output_mapping)

    def places(self):
        """Места проведения событий.

        Returns:
            list: Список словарей с информацией о месте проведения событий.
        """
        method = 'GetLocationList'
        input_mapping = None
        data = None
        output_mapping = {
            # Идентификатор места
            'cod_t':       self.internal('place_id', int,),
            # Название места
            'name_t':      self.internal('place_title', str,),
            # Код возврата
            'result_code': self.internal('result_code', int,),

            'tel_t':     None,
            'address_t': None,
            'city':      None,
        }
        places = self.request(method, input_mapping, data, output_mapping)

        if isinstance(places, list):
            places = sorted(places, key=itemgetter('place_id'))
        else:
            places = []

        return places

    def schemes(self, **kwargs):
        """Схемы залов в конкретном месте проведения событий.

        Args:
            place_id (int): Идентификатор места проведения событий.

        Returns:
            list: Список словарей с информацией о схеме залах.
        """
        method = 'GetHallList'
        input_mapping = {
            'cod_t': 'place_id',
        }
        data = kwargs
        output_mapping = {
            # Идентификатор зала
            'cod_th':      self.internal('scheme_id', int, 0,),
            # Название зала
            'name_h':      self.internal('scheme_title', str,),
            # Код возврата
            'result_code': self.internal('result_code', int,),

            'name_h2':   None,
            'tel_h':     None,
            'address_h': None,
        }
        schemes = self.request(method, input_mapping, data, output_mapping)

        if isinstance(schemes, list):
            schemes = sorted(schemes, key=itemgetter('scheme_id'))
        else:
            schemes = []

        return schemes

    def discover_schemes(self):
        """Получение списка схем залов для записи в БД.

        Недостающая информация добавляется из мест проведения событий ``places``.

        Returns:
            list: Список словарей с информацией о схеме зала.
        """
        discovered_schemes = []
        places = self.places()
        for p in places:
            if p['result_code'] == 0:
                schemes = self.schemes(place_id=p['place_id'])
                if isinstance(schemes, list):
                    for s in schemes:
                        # Формирование названия схемы зала
                        s['scheme_title'] = '{place_title} ({scheme_title})'.format(
                            place_title=p['place_title'],
                            scheme_title=s['scheme_title'].lower()
                        )
                        del s['result_code']
                        discovered_schemes.append(s)

                    discovered_schemes = sorted(discovered_schemes, key=itemgetter('scheme_id'))

        return discovered_schemes

    def groups(self):
        """Группы событий ("шоу" в терминологии СуперБилет).

        В СуперБилет каждое событие находится в своём "шоу", даже если это событие только в одном экземпляре.

        Returns:
            list: Список словарей с информацией о группах событий.
        """
        method = 'GetShowList'
        input_mapping = None
        data = None
        output_mapping = {
            # Идентификатор группы событий
            'cod_show':    self.internal('group_id', int,),
            # Название группы событий
            'name_show':   self.internal('group_title', str,),
            # Описание группы событий
            'annotation':  self.internal('group_text', str, ''),
            # Код ответа
            'result_code': self.internal('result_code', int,),

            'actors':      None,
            'author':      None,
            'cod_ganr':    None,
            'cod_categ':   None,
            'duration':    None,
            'name_show2':  None,
            'name_ganr':   None,
            'name_categ':  None,
            'note1':       None,
            'note2':       None,
            'note3':       None,
            'producer':    None,
            # СуперБилет Театр
            'autor':            None,
            'ispremiere':       None,
            'withintermission': None,
        }
        groups = self.request(method, input_mapping, data, output_mapping)

        if isinstance(groups, list):
            groups = sorted(groups, key=itemgetter('group_id'))
        else:
            groups = []

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
        if isinstance(events, list):
            for e in events:
                events_by_groups[(e['group_id'])].append(e)
            # Для сохранения в БД остаются только группы, содержащие более одного события
            # Единственное событие в группе рассматривается как самостоятельное событие без включения в группу.
            for i in list(events_by_groups):
                if len(events_by_groups[i]) <= 1:
                    del events_by_groups[i]
            groups[:] = [g for g in groups if g['group_id'] in events_by_groups.keys() and g['result_code'] == 0]
        else:
            events = []

        # Добавление в группу недостающей информации из самого раннего на данный момент входящего в неё события
        if isinstance(groups, list):
            for g in groups:
                for e in events:
                    if g['group_id'] == e['group_id']:
                        if g['group_text'] == '':
                            g['group_text'] = events_by_groups[(e['group_id'])][0]['event_text']
                        g['group_datetime'] = events_by_groups[(e['group_id'])][0]['event_datetime']
                        g['group_min_price'] = events_by_groups[(e['group_id'])][0]['event_min_price']
                        g['scheme_id'] = events_by_groups[(e['group_id'])][0]['scheme_id']
                del g['result_code']

            # Сортировка групп по дате/времени
            groups = sorted(groups, key=itemgetter('group_datetime'))
        else:
            groups = []

        return groups

    def events(self, **kwargs):
        """Список событий.

        Args:
            place_id (int): Идентификатор места проведения событий.
            scheme_id (int): Идентификатор схемы зала.

        Returns:
            list: Список словарей с информацией о событиях.
        """
        method = 'GetEventList'
        input_mapping = {
            'cod_t':  'place_id',
            'cod_th': 'scheme_id',
        }
        data = kwargs
        output_mapping = {
            # Идентификатор события
            'nombilkn':    self.internal('event_id', int,),
            # Название события
            'name_show':   self.internal('event_title', str,),
            # Дата события (локальное) '24.10.2017'
            'eventdate':   self.internal('event_date', str,),
            # Время события (локальное) '19:00:00'
            'eventtime':   self.internal('event_time', str,),
            # Описание события
            'annotation':  self.internal('event_text', str, ''),
            # Минимальная цена билета в событии
            'minprice':    self.internal('event_min_price', Decimal, self.decimal_price(0)),
            # Идентификатор группы
            'cod_show':    self.internal('group_id', int,),
            # Идентификатор места
            'cod_t':       self.internal('place_id', int),
            # Идентификатор схемы зала
            'cod_h':       self.internal('scheme_id', int,),
            # Примечание № 1 - ограничение по возрасту (строка, например, '12+')
            'note1':       self.internal('event_min_age', str,),
            # Примечание № 2 - организатор
            'note2':       self.internal('promoter', str,),
            # Код возврата
            'result_code': self.internal('result_code', int,),

            'actors':           None,
            'author':           None,
            'cod_ganr':         None,
            'cod_cate':         None,
            'eventduration':    None,
            'eventnote':        None,
            'is_primera':       None,
            'maxprice':         None,
            'maxpricesell':     None,
            'maxpricediscount': None,
            'minpricesell':     None,
            'minpricediscount': None,
            'name_ganr':        None,
            'name_categ':       None,
            'note3':            None,
            'note4':            None,
            'producer':         None,
            # СуперБилет Театр
            'num_web':       None,
            'num_boxoffice': None,
        }
        events = self.request(method, input_mapping, data, output_mapping)

        if isinstance(events, list):
            for e in events:
                if e['result_code'] == 0:
                    del e['place_id']
                    del e['result_code']
                else:
                    del events[e]

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

                # Получение остальных параметров либо значения по умолчанию
                if 'event_text' not in e:
                    e['event_text'] = ''

                if 'event_min_price' not in e:
                    e['event_min_price'] = self.decimal_price(0)

                e['event_min_age'] = (
                    int(e['event_min_age'][:-1]) if
                    'event_min_age' in e and e['event_min_age'].endswith('+') else
                    0
                )

                if 'promoter' not in e:
                    e['promoter'] = ''

            events = sorted(events, key=itemgetter('event_datetime'))
        else:
            events = []

        return events

    def discover_events(self):
        """Получение списка событий для записи в БД (с включением недостающей информации из групп событий).

        Returns:
            list: Список словарей с информацией о событиях.
        """
        return self.events()

    def sectors(self, **kwargs):
        """Список секторов в конкретном событии.

        Args:
            event_id (int): Идентификатор события.

        Returns:
            dict: Словарь, где ключи - идентификаторы секторов, значения - названия секторов.
        """
        method = 'GetSectorList'
        input_mapping = {
            'NomBilKn': 'event_id',
        }
        data = kwargs
        output_mapping = {
            # Идентификатор сектора
            'cod_sec':     self.internal('sector_id', int,),
            # Название сектора
            'name_sec':    self.internal('sector_title', str,),
            # Общее число мест в секторе
            'placescount': self.internal('seats_all_count', int,),  # только в СуперБилет Агентство
            # Код возврата
            'result_code': self.internal('result_code', int,),

            'nombilkn': None,
        }
        sectors = self.request(method, input_mapping, data, output_mapping)

        if isinstance(sectors, list):
            sectors = {s['sector_id']: s['sector_title'].lower() for s in sectors}

        return sectors

    def seats_and_prices(self, **kwargs):
        """Доступные для продажи места в событии и список цен на билеты.

        Args:
            event_id (int): Идентификатор события.

        Returns:
            dict: Словарь, содержащий словарь ``seats`` и список ``prices``.
        """
        method = 'GetEvailPlaceList'
        input_mapping = {
            'NomBilKn': 'event_id',
        }
        data = kwargs
        output_mapping = {
            # Идентификатор места
            'seat':        self.internal('seat_id', int,),
            # Идентификатор ряда
            'row':         self.internal('row_id', int,),
            # Идентификатор сектора
            'cod_sec':     self.internal('sector_id', int,),
            # Цена
            'price':       self.internal('price', Decimal,),
            # Код возврата
            'result_code': self.internal('result_code', int,),

            'nombilkn':      None,
            'pricesell':     None,  # Цена продажи
            'pricediscount': None,  # Цена продажи со скидкой
            # СуперБилет Театр
            'cod_hs':        None,  # Объект на схеме зала из метода `scheme`
        }
        sectors = self.sectors(event_id=kwargs['event_id'])
        seats = self.request(method, input_mapping, data, output_mapping)

        response = {}
        response['seats'] = {}
        response['prices'] = []

        if isinstance(seats, list):
            response['success'] = True

            # Получение списка цен на билеты, упорядоченного по возрастанию
            seats_by_prices = defaultdict(list)
            for s in seats:
                seats_by_prices[(s['price'])].append(s)

            prices = sorted([p for p in seats_by_prices])
            response['prices'] = prices

            # Получение перечня свободных для продажи мест
            for s in seats:
                if s['result_code'] == 0:
                    seat = {}
                    # Уникальный идентификатор билета
                    ticket_id = self._compose_ticket_id(s['sector_id'], s['row_id'], s['seat_id'])

                    seat['sector_id'] = s['sector_id']
                    # Название сектора (если оно получено без ошибок)
                    seat['sector_title'] = (
                        sectors.get(s['sector_id']) if
                        isinstance(sectors, dict) and 'error' not in sectors else
                        ''
                    )
                    seat['row_id'] = s['row_id']
                    seat['seat_id'] = s['seat_id']
                    seat['seat_title'] = str(s['seat_id'])
                    seat['price'] = s['price']
                    # Порядковые номера цен на билеты для сопоставления с цветом места в схеме зала
                    seat['price_order'] = prices.index(s['price']) + 1 if len(prices) > 0 else 0

                    response['seats'][ticket_id] = seat

            del seats
        else:
            response['success'] = False

            response['code'] = seats['code']
            response['message'] = seats['message']

        return response

    def sector_seats(self, **kwargs):
        """Доступные места в конкретном секторе в конкретном событии.

        Args:
            event_id (int): Идентификатор события.
            sector_id (int): Идентификатор сектора.

        Returns:
            list: Вызов конструктора запросов request.
        """
        method = 'GetPlaceForSector'
        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
        }
        data = kwargs
        output_mapping = {
            # Идентификатор сектора
            'cod_sec':     self.internal('sector_id', int,),
            # Идентификатор ряда
            'row':         self.internal('row_id', int,),
            # Идентификатор места
            'seat':        self.internal('seat_id', int,),
            # Цена
            'price':       self.internal('price', Decimal,),
            # Код возврата
            'result_code': self.internal('result_code', int,),

            'cod_hs':        None,  # Объект на схеме зала из метода `scheme`
            'name_sector':   None,
            'nombilkn':      None,
            'pricesell':     None,  # Цена продажи
            'pricediscount': None,  # Цена продажи со скидкой
        }
        sector_seats = self.request(method, input_mapping, data, output_mapping)

        if isinstance(sector_seats, list):
            sector_seats = sorted(sector_seats, key=itemgetter('price', 'sector_id', 'row_id', 'seat_id'))

        return sector_seats

    def reserve(self, **kwargs):
        """Добавление или удаление места в предварительном резерве мест (корзина заказа).

        Args:
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID как номер сессии (любая строка до 50 однобайтовых символов).
            ticket_id (str): Идентификатор билета (``сектор_ряд_место``).
            action (str): Действие (``add`` - добавить в резерв, ``remove`` - удалить из резерва).

        Returns:
            dict: Атрибуты места с подтверждением успешного или НЕуспешного резерва.
        """
        if kwargs['action'] == 'add':
            method = 'PreSetReservation'
        elif kwargs['action'] == 'remove':
            method = 'FreePreReservation'

        # Разбиваем идентификатор билета на составляющие, чтобы отправить их в отдельных переменных
        kwargs['sector_id'], kwargs['row_id'], kwargs['seat_id'] = self._decompose_ticket_id(kwargs['ticket_id'])

        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'row':      'row_id',
            'seat':     'seat_id',
            'session':  'order_uuid',
        }
        data = kwargs
        output_mapping = {
            'session':     self.internal('order_uuid', str,),
            'cod_sec':     self.internal('sector_id', int,),
            'row':         self.internal('row_id', int,),
            'seat':        self.internal('seat_id', int,),
            'price':       self.internal('price', Decimal,),
            'result_code': self.internal('result_code', int,),

            'nombilkn':      None,
            'pricesell':     None,
            'pricediscount': None,
        }
        reserve = self.request(method, input_mapping, data, output_mapping)

        response = {}

        if isinstance(reserve, list) and reserve[0]['result_code'] == 0:
            response['success'] = True

            response['event_id'] = kwargs['event_id']
            response['order_uuid'] = kwargs['order_uuid']
            response['ticket_id'] = kwargs['ticket_id']
            response['action'] = kwargs['action']
        else:
            response['success'] = False

            response['code'] = reserve['code']
            response['message'] = reserve['message']

        return response

    def ticket_status(self, **kwargs):
        """Проверка состояния места (перед созданием заказа или перед онлайн-оплатой).

        В новой версии СуперБилет НЕ работает корректно, если передано несколько мест для проверки состояния.

        При попытке получить статус свободного в продаже места СуперБилет может ничего не возвратить...

        Args:
            event_id (int): Идентификатор события.
            ticket_id (str): Идентификатор билета (``сектор_ряд_место``).

            from_date (str, optional): Фильтр по начальной дате.
            to_date (str, optional): Фильтр по начальному времени.
            from_time (str, optional): Фильтр по конечной дате.
            to_time (str, optional): Фильтр по конечному времени.

        Returns:
            dict: Информация о состоянии места.

                Содержимое результата:
                    * **success** (bool): Успешный (``True``) или НЕуспешный (``False``) результат.
                    * **status** (str): Статус места, сопоставляемый из словаря ``SEAT_STATUSES``.
        """
        method = 'GetCurrentState'

        # Разбиваем идентификатор билета на составляющие, чтобы отправить их в отдельных переменных
        kwargs['sector_id'], kwargs['row_id'], kwargs['seat_id'] = self._decompose_ticket_id(kwargs['ticket_id'])

        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'Row':      'row_id',
            'Seat':     'seat_id',

            'DateFrom': 'from_date',
            'DateTo':   'to_date',
            'TimeFrom': 'from_time',
            'TimeTo':   'to_time',
        }
        data = kwargs
        output_mapping = {
            'nombilkn':       self.internal('event_id', int,),
            'session':        self.internal('order_uuid', str,),
            'reservid':       self.internal('order_id', int,),
            'transactionid':  self.internal('payment_id', str,),

            'cod_sec':        self.internal('sector_id', int,),
            'row':            self.internal('row_id', int,),
            'seat':           self.internal('seat_id', int,),
            'gatestatus':     self.internal('status', str,),

            'result_code':    self.internal('result_code', int,),

            'actiondate':     None,
            'actiontime':     None,
            'gateactiondate': None,
            'gateactiontime': None,
            'gatereservid':   None,
            'gateuser':       None,  # bool установлен ли последний статус текущим пользователем шлюза
            'idspectator':    None,  # ???
            'price':          None,
            'pricesell':      None,
            'pricediscount':  None,
            'paymentdate':    None,
            'status':         None,
        }
        status = self.request(method, input_mapping, data, output_mapping)
        print(kwargs['ticket_id'], ' status: ', status)

        response = {}

        if isinstance(status, list) and status[0]['result_code'] == 0:
            status = {k: v for k, v in status[0].items()}

            response['success'] = True
            response['status'] = (
                self.SEAT_STATUSES['FREE'] if
                status['status'] == '' else
                self.SEAT_STATUSES[status['status']]
            )
        else:
            response['success'] = False

            response['code'] = status['code']
            response['message'] = status['message']

        return response

    def order_create(self, **kwargs):
        """Создание заказа из предварительно зарезервированных мест.

        Агентство вызывает обычный метод, а Театр вызывает Ext-метод с одними и теми же аргументами.
        При попытка запуска Ext-метода в Агентстве приходила ошибка ``2 "Ошибка интерфейса - неверный формат данных"``.

        Args:
            event_id (int): Идентификатор события.
            order_uuid (uuid.UUID): Уникальный UUID как номер сессии (любая строка до 50 однобайтовых символов).
            customer (dict): Реквизиты покупателя.
            tickets (dict): Словарь, содержащий словари с параметрами заказываемых билетов.

        Customer keys:
            name (str): ФИО покупателя.
            email (str): Электронная почта покупателя.
            phone (str): Телефон покупателя.
            is_courier (bool): Нужна ли доставка или нет.
            address (str): Адрес доставки (если она нужна).

        Tickets keys:
            sector_id (int): Идентификатор сектора.
            row_id (int): Идентификатор ряда.
            seat_id (int): Идентификатор места.

        Returns:
            dict: Список словарей с информацией о билетах в заказе.

                Содержимое результата:
                    order_id (int): Идентификатор заказа в сервисе заказа билетов.
                    tickets (dict): Словарь, содержащий словари с информацией о заказанных билетах.

                        Содержимое словарей в **tickets**:
                            ticket_uuid (uuid.UUID): Уникальный UUID билета.
                            bar_code (str): Штрих-код билета (20 символов).
        """
        if self.__mode == 'agency':
            method = 'SetReservation'
        elif self.__mode == 'theatre':
            method = 'SetReservationExt'
        input_mapping = {
            'NomBilKn': 'event_id',

            'NameSpektator':  'name',
            'TelSpektator':   'phone',
            'EmailSpektator': 'email',
            'Delivery':       'is_courier',
            'Address':        'address',

            'cod_sec': 'sector_id',
            'row':     'row_id',
            'seat':    'seat_id',
            'Session': 'order_uuid',
        }
        # Формирование списка билетов для отправки и объединение всех входных параметров в каждом билете в этом списке
        tickets_input = []
        for ticket_id in kwargs['tickets']:
            kwargs['tickets'][ticket_id]['event_id'] = kwargs['event_id']
            kwargs['tickets'][ticket_id]['order_uuid'] = kwargs['order_uuid']
            kwargs['tickets'][ticket_id]['name'] = kwargs['customer']['name']
            kwargs['tickets'][ticket_id]['email'] = kwargs['customer']['email']
            kwargs['tickets'][ticket_id]['phone'] = kwargs['customer']['phone']
            kwargs['tickets'][ticket_id]['is_courier'] = '1' if kwargs['customer']['is_courier'] else '0'
            kwargs['tickets'][ticket_id]['address'] = (
                kwargs['customer']['address'] if kwargs['customer']['is_courier'] else ''
            )
            tickets_input.append(kwargs['tickets'][ticket_id])
        data = tickets_input
        output_mapping = {
            'namespektator':  self.internal('name', str,),
            'telspektator':   self.internal('phone', str,),
            'emailspektator': self.internal('email', str,),
            'delivery':       self.internal('is_courier', bool,),
            'address':        self.internal('address', str,),

            'session':        self.internal('order_uuid', str,),
            'reservid':       self.internal('order_id', int, 0),
            'cod_sec':        self.internal('sector_id', int,),
            'row':            self.internal('row_id', int,),
            'seat':           self.internal('seat_id', int,),

            'result_code':    self.internal('result_code', int,),

            'idspectator':    None,
            'nombilkn':       None,
            'reservdate':     None,
            'price':          None,
            'pricesell':      None,
            'pricediscount':  None,
            'metro':          None,
            'notes':          None,
            'orderid':        None,  # ID доставки ???
        }
        if self.__mode == 'agency':
            output_mapping['orderbarcode'] = self.internal('bar_code', str, '')
        elif self.__mode == 'theatre':
            output_mapping['barcode'] = self.internal('bar_code', str, '')

        order_created = self.request(method, input_mapping, data, output_mapping)
        # self.logger.info('\norder response: {}'.format(order))

        # order []:
        # 'order_uuid': '1fa590a2-21e4-453a-ab5a-945e422ac42c',
        # 'sector_id': 509,
        # 'row_id': 19,
        # 'seat_id': 44
        # 'bar_code': '01564651417635228226',

        response = {}
        response['tickets'] = {}

        if isinstance(order_created, list):
            for ot in order_created:
                # Уникальный идентификатор билета
                ot['ticket_id'] = self._compose_ticket_id(ot['sector_id'], ot['row_id'], ot['seat_id'])

                if ot['result_code'] == 0:
                    # Идентификатор заказа берётся из списка удачно заказанных билетов
                    # В одном заказе он будет один и тот же
                    response['success'] = True
                    response['order_id'] = ot['order_id']
                    for ticket_id in kwargs['tickets']:
                        if ot['ticket_id'] == kwargs['tickets'][ticket_id]['ticket_id']:
                            # self.logger.info('    {ot_ticket_id} == {t_ticket_id}: {cond}'.format(
                            #     ot_ticket_id=ot['ticket_id'],
                            #     t_ticket_id=kwargs['tickets'][ticket_id]['ticket_id'],
                            #     cond=ot['ticket_id'] == kwargs['tickets'][ticket_id]['ticket_id'])
                            # )
                            ticket = {}
                            ticket['ticket_uuid'] = kwargs['tickets'][ticket_id]['ticket_uuid']
                            ticket['bar_code'] = ot['bar_code']
                            response['tickets'][ticket_id] = ticket.copy()
                        else:
                            continue
        else:
            response['success'] = False
            del response['tickets']

            response['code'] = order_created['code']
            response['message'] = order_created['message']

        del order_created

        return response

    def order_cancel(self, **kwargs):
        """Отмена ранее созданного заказа.

        Args:
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID как номер сессии (любая строка до 50 однобайтовых символов).
            order_id (int): Идентификатор заказа.
            tickets (dict): Словарь, содержащий словари с параметрами заказываемых билетов.

        Returns:
            dict: Информация об удалении заказа.

                Содержимое результата:
                    * **success** (bool): Успешный (``True``) или НЕуспешный (``False``) результат.
        """
        method = 'FreeReservation'
        input_mapping = {
            'session':  'order_uuid',
            'reservID': 'order_id',
            'NomBilKn': 'event_id',

            'cod_sec':  'sector_id',
            'row':      'row_id',
            'seat':     'seat_id',
        }
        # Формирование списка билетов для отправки и объединение всех входных параметров в каждом билете в этом списке
        tickets_input = []
        for ticket_id in kwargs['tickets']:
            ticket = {}
            ticket['sector_id'] = kwargs['tickets'][ticket_id]['sector_id']
            ticket['row_id'] = kwargs['tickets'][ticket_id]['row_id']
            ticket['seat_id'] = kwargs['tickets'][ticket_id]['seat_id']
            ticket['event_id'] = kwargs['event_id']
            ticket['order_uuid'] = kwargs['order_uuid']
            ticket['order_id'] = kwargs['order_id']
            tickets_input.append(ticket)
        data = tickets_input
        output_mapping = {
            'session':     self.internal('order_uuid', str,),
            'reservid':    self.internal('order_id', str,),

            'cod_sec':     self.internal('sector_id', int,),
            'row':         self.internal('row_id', int,),
            'seat':        self.internal('seat_id', int,),

            'result_code': self.internal('result_code', int,),

            'nombilkn':    None,
            'reservdate':  None,
            'price':       None,
        }
        cancel = self.request(method, input_mapping, data, output_mapping)
        # print('cancel:', cancel)

        response = {}

        if isinstance(cancel, list):
            for c in cancel:
                if 'result_code' in c and c['result_code'] == 0:
                    response['success'] = True
                else:
                    response['success'] = False
                    response['code'] = c['result_code']
                    response['message'] = c['message']
        else:
            response['success'] = False

            response['code'] = cancel['code']
            response['message'] = cancel['message']

        return response

    def order_approve(self, **kwargs):
        """Отметка о подтверждении онлайн-оплаты созданного ранее заказа.

        Агентство вызывает обычный метод, а Театр вызывает Ext-метод с одними и теми же аргументами.

        Args:
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID как номер сессии (любая строка до 50 однобайтовых символов).
            order_id (int): Идентификатор заказа.
            payment_id (int): Идентификатор оплаты.
            payment_datetime (datetime.datetime): Дата и время оплаты.
            tickets (dict): Словарь, содержащий словари с параметрами заказываемых билетов.

        Returns:
            dict: Информация об успешной или НЕуспешной оплате.

                Содержимое результата:
                    * **success** (bool): Успешный (``True``) или НЕуспешный (``False``) результат.
        """
        if self.__mode == 'agency':
            method = 'SetSold'  # SetSoldExt
        elif self.__mode == 'theatre':
            method = 'SetSoldExt'
        input_mapping = {
            'NomBilKn': 'event_id',
            'cod_sec':  'sector_id',
            'row':      'row_id',
            'seat':     'seat_id',
            'session':  'order_uuid',

            'TransactionID': 'payment_id',
            'PaymentDate':   'payment_date',
            'PaymentTime':   'payment_time',
        }
        # Формирование списка билетов для отправки и объединение всех входных параметров в каждом билете в этом списке
        tickets_input = []
        for ticket_id in kwargs['tickets']:
            ticket = {}
            ticket['sector_id'] = kwargs['tickets'][ticket_id]['sector_id']
            ticket['row_id'] = kwargs['tickets'][ticket_id]['row_id']
            ticket['seat_id'] = kwargs['tickets'][ticket_id]['seat_id']
            ticket['event_id'] = kwargs['event_id']
            ticket['order_uuid'] = kwargs['order_uuid']
            ticket['payment_id'] = kwargs['payment_id']
            ticket['payment_date'] = kwargs['payment_datetime'].strftime('%d.%m.%Y')
            ticket['payment_time'] = kwargs['payment_datetime'].strftime('%H:%M:%S')
            tickets_input.append(ticket)
        data = tickets_input
        output_mapping = {
            'session':        self.internal('order_uuid', str,),
            'reservid':       self.internal('order_id', int,),    # в случае ошибки = 0

            'cod_sec':        self.internal('sector_id', int,),
            'row':            self.internal('row_id', int,),
            'seat':           self.internal('seat_id', int,),

            'result_code':    self.internal('result_code', int,),

            'nombilkn':       None,
            'pricesell':      None,
            'pricediscount':  None,
            'reservdate':     None,  # в случае ошибки = ''
            'price':          None,  # в случае ошибки = 0
            'transactionid':  None,
            'paymentdate':    None,
            'paymenttime':    None,
        }
        approve = self.request(method, input_mapping, data, output_mapping)

        response = {}

        if isinstance(approve, list):
            for a in approve:
                if 'result_code' in a and a['result_code'] == 0:
                    response['success'] = True
                else:
                    response['success'] = False
                    response['code'] = a['result_code']
                    response['message'] = a['message']
        else:
            response['success'] = False

            response['code'] = approve['code']
            response['message'] = approve['message']

        del approve

        return response

    # def order_pre_payment_check(self, tickets):
    #     """Проверка заказа перед оплатой.

    #     Args:
    #         tickets (list): Список словарей с параметрами заказываемого места.

    #     Tickets attributes:
    #         event_id (int): Идентификатор события.
    #         sector_id (int): Идентификатор сектора.
    #         row_id (int): Идентификатор ряда.
    #         seat_id (int): Идентификатор места.
    #         order_uuid (str): Уникальный UUID как номер сессии (любая строка до 50 однобайтовых символов).
    #         order_id (int): Идентификатор заказа.

    #         payment_id (int): Идентификатор оплаты.
    #         payment_date (str): Дата оплаты.
    #         payment_time (str): Время оплаты.

    #         user (str): Логин пользователя шлюза.
    #         pswd (str): Пароль пользователя шлюза.

    #     Returns:
    #         method: Вызов конструктора запросов request.
    #     """
    #     method = 'CheckSoldTickets'
    #     input_mapping = {
    #         'NomBilKn':      'event_id',
    #         'cod_sec':       'sector_id',
    #         'row':           'row_id',
    #         'seat':          'seat_id',
    #         'session':       'order_uuid',
    #         'reservID':      'order_id',

    #         'TransactionID': 'payment_id',
    #         'PaymentDate':   'payment_date',
    #         'PaymentTime':   'payment_time',

    #         'Login':         'user',
    #         'Password':      'pswd',
    #     }
    #     data = tickets
    #     output_mapping = {
    #         'session':     self.internal('order_uuid', str,),
    #         'cod_sec':     self.internal('sector_id', int,),
    #         'row':         self.internal('row_id', int,),
    #         'seat':        self.internal('seat_id', int,),
    #         'reservid':    self.internal('order_id', str,),
    #         'price':       self.internal('price', Decimal,),
    #         'result_code': self.internal('result_code', int,),

    #         'nombilkn':    None,
    #     }
    #     return self.request(method, input_mapping, data, output_mapping)

    # SetSoldTickets(Login, Password, Value) -> return: xsd:string

    # Отличия в параметрах нового метода SetSoldTickets от старого метода SetSoldExt:
    # 1. Логин и пароль в новых методах передается отдельными параметрами вызова, а не внутри входного xml
    # 2. Параметр session переименован в sessionID
    # 3. Новый обязательный входной параметр ReservID
    # 4. Новый обязательный входной параметр price

    def order_refund(self, **kwargs):
        """Возврат стоимости билетов (с удалением заказа и освобождением билетов для продажи).

        Возвраты в СуперБилет НЕ делаются - метод оставлен для обратной совместимости.
        Освободить места для продажи в случае возврата сейчас можно только в программе для кассиров.

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
        response = {}
        response['success'] = True
        response['amount'] = kwargs['amount'] if 'amount' in kwargs else Decimal(0.00)

        return response

    def scheme(self, **kwargs):
        """Схема зала для события/сектора.

        Args:
            event_id (int): Идентификатор события.

        Returns:
            method: Вызов конструктора запросов request.
        """
        method = 'GetSchemaHallList'
        input_mapping = {
            'NomBilKn': 'event_id',
        }
        data = kwargs
        output_mapping = {
            'cod_hs': self.internal('object_id', int,),
            'objectid': self.internal('object_type_id', int,),  # 0 - кресло, 1 - точка линии, 2 - метка
            'objectname': self.internal('object_type_title', str,),  # Place - кресло, Point - точка линии, Label - метка
            'placesize': self.internal('scheme_size', int,),  # 22 или 15
            'width': self.internal('object_width', int,),  # Ширина кресла (0 для остальных объектов)
            'height': self.internal('object_height', int,),  # Высота кресла (0 для остальных объектов)
            'pointindex': self.internal('point_index', int,),  # Индекс точки в пределах одной линии
            'grouppointindex': self.internal('group_point_index', int,),  # Индекс линии в пределах зала
            'cx': self.internal('object_x', int,),  # Координата объекта по оси X
            'cy': self.internal('object_y', int,),  # Координата объекта по оси Y
            'angel': self.internal('object_angle', int,),  # Угол поворота кресла (0 для остальных объектов)
            'row': self.internal('row_id', int,),  # Ряд
            'seat': self.internal('seat_id', int,),  # Место
            'cod_sec': self.internal('sector_id', int,),  # ID сектора
            'name_sec': self.internal('sector_title', str,),  # Наименование сектора
            'label': self.internal('object_label', str,),  # Текст метки
            'backcolor': self.internal('object_background', str,),  # Цвет фона метки (FFFFFF для прозрачного фона)
            'fontcolor': self.internal('object_color', str,),  # Цвет шрифта метки или цвет линии
            'fontsize': self.internal('object_font_size', int,),  # Размер шрифта метки
            'imageindex': self.internal('object_image_index', int,),  # Индекс картинки метки
            'minx': self.internal('object_min_x', int,),  # Минимальная координата зала по оси X
            'miny': self.internal('object_min_y', int,),  # Минимальная координата зала по оси Y
            'maxx': self.internal('object_max_x', int,),  # Максимальная координата зала по оси X
            'maxy': self.internal('object_max_y', int,),  # Максимальная координата зала по оси Y
            'nombilkn': None,
        }
        return self.request(method, input_mapping, data, output_mapping)

    def log(self, **kwargs):
        """Журнал операций СуперБилета (обычный или расширенный).

        Args:
            event_id (int): Идентификатор события.
            sector_id (int): Идентификатор сектора.
            row_id (int): Идентификатор ряда.
            seat_id (int): Идентификатор места.

            from_date (str): Фильтр по начальной дате.
            to_date (str): Фильтр по начальному времени.
            from_time (str): Фильтр по конечной дате.
            to_time (str): Фильтр по конечному времени.

        Returns:
            method: Вызов конструктора запросов request.
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
            'actiondate':     self.internal('date', str,),
            'actiontime':     self.internal('time', str,),
            'actiondone':     self.internal('operation', str,),
            'nombilkn':       self.internal('event_id', int,),
            'cod_sec':        self.internal('sector_id', int,),
            'row':            self.internal('row_id', int,),
            'seat':           self.internal('seat_id', int,),
            'price':          self.internal('price', Decimal,),
            'reservid':       self.internal('order_id', int, 0,),

            'session':        self.internal('order_uuid', str,),
            'idspectator':    self.internal('customer_id', str, 0,),  # ???
            'namespectator':  self.internal('name', str,),
            'telspectator':   self.internal('phone', str,),
            'emailspectator': self.internal('email', str,),

            'result_code':    self.internal('result_code', int,),

            'gateactiondate': None,
            'gateactiontime': None,
            'gateuser':       None,
            'reservdate':     None,
            'pricesell':      None,
            'pricediscount':  None,
        }
        log = self.request(method, input_mapping, data, output_mapping)

        if isinstance(log, list):
            for l in log:
                # Преобразование даты/времени
                date, month, year = l['date'].split('.')
                event_datetime = '{year}-{month}-{date} {time}'.format(
                    year=year,
                    month=month,
                    date=date,
                    time=l['time']
                )
                l['datetime'] = datetime.strptime(event_datetime, '%Y-%m-%d %H:%M:%S')
                del l['date']
                del l['time']

                # Добавление описания операции из словаря LOG_OPERATIONS
                try:
                    l['description'] = self.LOG_OPERATIONS[l['operation']]
                except KeyError:
                    l['description'] = ''

            log = sorted(log, key=itemgetter('datetime'))
        else:
            return log

        return log

    def _compose_ticket_id(self, sector_id, row_id, seat_id):
        """Получение идентификатора билета (сочетание идентификаторов сектора, ряда и места).

        Args:
            sector_id (int): Идентификатор сектора.
            row_id (int): Идентификатор ряда.
            seat_id (int): Идентификатор места.

        Returns:
            str: Идентификатор билета.
        """
        return '{sector_id}_{row_id}_{seat_id}'.format(
            sector_id=sector_id,
            row_id=row_id,
            seat_id=seat_id
        )

    def _decompose_ticket_id(self, ticket_id):
        """Разбор полученного ранее идентификатора билета на идентификаторы сектора, ряда и места.

        Args:
            ticket_id (str): Идентификатор билета.

        Returns:
            list: Список параметров билета.
        """
        ticket_id_items = ticket_id.split('_')
        return [int(i) for i in ticket_id_items]

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
