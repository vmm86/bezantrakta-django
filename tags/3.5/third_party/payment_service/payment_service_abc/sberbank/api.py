import dateutil.parser
import requests
import simplejson as json
from datetime import datetime
from decimal import Decimal

try:
    from project.shortcuts import BOOLEAN_VALUES
except ImportError:
    BOOLEAN_VALUES = ('True', 'true', 1, '1', 'y', 'yes', 'д', 'да',)

from ..abc import PaymentService


class Sberbank(PaymentService):
    """Класс для работы с API Сбербанка.

    Любой метод, делающий запросы к API, вызывает для этого конструктор запросов ``request``.

    Атрибуты класса:
        **slug** (str): Псевдоним для инстанцирования класса (``sberbank``).

    Attributes:
        commission (Decimal): Процент комиссии.
        timeout (int): Таймаут до завершения оплаты в минутах (по умолчанию - **15 минут**).
    """
    slug = 'sberbank'

    # Базовый URL для отправки запросов к API тестовой или настоящей оплаты
    __TEST_HOST = 'https://3dsec.sberbank.ru/payment/rest/'
    __PROD_HOST = 'https://securepayments.sberbank.ru/payment/rest/'

    # Коды статуса оплаты в ответе self.payment_status
    PAYMENT_STATUS_CODES = {
        0: 'Заказ зарегистрирован, но пока не оплачен',
        1: 'Предавторизованная сумма захолдирована (для 2-стадийных платежей)',
        2: 'Проведена полная авторизация суммы заказа',
        3: 'Авторизация отменена',
        4: 'Была проведён возврат',
        5: 'Инициирована авторизация через ACS банка-эмитента',
        6: 'Авторизация отклонена',
    }

    # Сообщения о статусе оплаты в ответе self.payment_status
    PAYMENT_STATUS_MESSAGES = {
        'CREATED':   'созданный запрос на оплату',
        'APPROVED':  'удержание (холдирование) суммы при 2-хстадийной оплате',
        'DEPOSITED': 'успешно завершено',
        'DECLINED':  'отклонено',
        'REVERSED':  'отмена платежа',
        'REFUNDED':  'возврат платежа',
    }

    def __init__(self, init):
        """Конструктор класса.

        Args:
            init (dict): Словарь с параметрами для инстанцирования класса.

                Содержимое ``init``:
                    * **mode** (str): Тестовая или настоящая оплата
                    * **user** (str): Пользователь для доступа к API.
                    * **test_pswd** (str): Пароль для тестового доступа к API.
                    * **prod_pswd** (str): Пароль для production-доступа к API.
                    * **success_url** (str): URL для обработки удачной оплаты.
                    * **error_url** (str): URL для обработки НЕудачной оплаты.
                    * **commission** (float): Комиссия (преобразуется в ``Decimal``).
                    * **timeout** (int): Время сессии на оплату в минутах (по умолчанию - **15 минут**).
        """
        super().__init__()

        # Параметры подключения
        self.__mode = init['mode']  # ('test', 'prod',)

        self.__user = init['user']

        if self.__mode == 'test':
            self.__host = Sberbank.__TEST_HOST
            self.__pswd = init['test_pswd']
        elif self.__mode == 'prod':
            self.__host = Sberbank.__PROD_HOST
            self.__pswd = init['prod_pswd']

        # URL для завершения заказа после удачной или НЕудачной оплаты
        self.__success_url = init['success_url'] if 'success_url' in init else None
        self.__error_url = init['error_url'] if 'error_url' in init else None

        # Дополнительные параметры
        self.commission = (
            self.decimal_price(init['commission']) if
            'commission' in init and self.decimal_price(init['commission']) > 0 else
            self.decimal_price(0.0)
        )
        self.timeout = init['timeout'] if 'timeout' in init and init['timeout'] > 0 else 15
        self.description = """
        <p>Оплата происходит через авторизационный сервер Процессингового центра Банка с использованием банковских кредитных карт следующих платёжных систем:</p>
        <p>
        <ul>
            <li><img src="/media/global/banner/banner_payment/type-mir.png" width="43" height="25" style="vertical-align: middle;"> <strong>МИР</strong>,</li>
            <li><img src="/media/global/banner/banner_payment/type-visa.png" width="43" height="25" style="vertical-align: middle;"> <strong>VISA International</strong>,</li>
            <li><img src="/media/global/banner/banner_payment/type-mc.png" width="43" height="25" style="vertical-align: middle;"> <strong>MasterCard World Wide</strong>.</li>
        </ul>
        </p>
        <p>Для оплаты покупки Вы будете перенаправлены на платежный шлюз ПАО "<strong>Сбербанк России</strong>" для ввода реквизитов Вашей карты. Соединение с платежным шлюзом и передача информации осуществляется в защищенном режиме с использованием протокола шифрования <strong>SSL</strong>.</p>
        <p>В случае если Ваш банк поддерживает технологию безопасного проведения Интернет-платежей Verified By Visa или MasterCard Secure Code, для проведения платежа также <strong>может потребоваться ввод специального пароля</strong>. Способы и возможность получения паролей для совершения Интернет-платежей Вы можете уточнить в банке, выпустившем карту.</p>
        <p>Настоящий сайт поддерживает 256-битное шифрование. Конфиденциальность сообщаемой персональной информации обеспечивается ПАО "<strong>Сбербанк России</strong>". Введённая информация не будет предоставлена третьим лицам за исключением случаев, предусмотренных законодательством РФ. Проведение платежей по банковским картам осуществляется в строгом соответствии с требованиями платежных систем <strong>МИР</strong>, <strong>Visa Int.</strong> и <strong>MasterCard Europe Sprl</strong>.</p>
        """

    def __str__(self):
        return '{cls}({user}: {mode})'.format(
            cls=self.__class__.__name__,
            user=self.__user,
            mode=self.__mode,
        )

    def request(self, method, url, data, output_mapping, test=False):
        """Конструктор запросов к API.

        Args:
            method (str): HTTP-метод (``GET`` или ``POST``).
            url (str): Относительный URL конкретного метода API.
            data (dict): Параметры запроса для GET или тело запроса для POST.
            output_mapping (dict): Сопоставление выходных параметров.
            test (bool, optional): Опциональный параметр для тестирования работы.

        Returns:
            list, dict: Обработанный ответ конкретного метода API.
        """
        url_path = self.__host + url

        # Параметры для авторизации любых запросов
        data['userName'] = self.__user
        data['password'] = self.__pswd

        if method == 'GET':
            response = requests.get(url_path, params=data)
        elif method == 'POST':
            response = requests.post(url_path, data=data)

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
        # Если в ответе - множество записей
        if type(response) is list:
            # Ключи в нижнем регистре
            iterable = [{k.lower(): v for k, v in r.items()} for r in response]
            # Конвертация ключей в человекопонятные значения
            for d in iterable:
                self.humanize_with_type_casting(d, output_mapping)
                d['success'] = True
        # Если в ответе - одна запись
        elif type(response) is dict:
            # Ключи в нижнем регистре
            iterable = {k.lower(): v for k, v in response.items()}
            # Конвертация ключей в человекопонятные значения
            self.humanize_with_type_casting(iterable, output_mapping)
            iterable['success'] = True

        # print('\nprettified response: ', iterable, '\n')

        # Успешный или НЕуспешный ответ
        if 'code' in iterable:
            if iterable['code'] == 0:
                response_success = True
                response_code = 0
                response_message = 'OK'
            else:
                response_success = False
                response_code = iterable['code']
                response_message = iterable['message']
        else:
            response_success = True
            response_code = 0
            response_message = 'OK'

        # Вывод успешного ответа или сообщения об ошибке
        return (
            iterable if
            response_success else
            {'success': False, 'code': response_code, 'message': response_message, }
        )

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
                        if internal.default is not None:
                            iterable[internal.key] = internal.default
                    # Если получено НЕпустое значение - приведение типов данных
                    else:
                        if internal.type is str and type(iterable[internal.key]) is not str:
                            iterable[internal.key] = str(internal.default)
                            # Если получена пустая строка - поиск значения по умолчанию
                            iterable[internal.key] == (
                                internal.default if
                                iterable[internal.key] == '' and internal.default is not None else
                                iterable[internal.key]
                            )
                        elif internal.type is int and type(iterable[internal.key]) is not int:
                            iterable[internal.key] = int(iterable[internal.key])
                        elif internal.type is bool and type(iterable[internal.key]) is not bool:
                            iterable[internal.key] = True if iterable[internal.key] in BOOLEAN_VALUES else False
                        elif internal.type is Decimal and type(iterable[internal.key]) is not Decimal:
                            iterable[internal.key] = self.decimal_price(iterable[internal.key])
                        elif internal.type is datetime and type(iterable[internal.key]) is not datetime:
                            iterable[internal.key] = dateutil.parser.parse(iterable[internal.key])
                        elif internal.type is list and len(iterable[internal.key]) > 0:
                            # Приведение ключей списка из словарей к нижнему регистру
                            if type(iterable[internal.key][0]) is dict:
                                iterable[internal.key] = [
                                    {k.lower(): v for k, v in i.items()} for i in iterable[internal.key]
                                ]
                        elif internal.type is dict and len(iterable[internal.key]) > 0:
                            # Приведение ключей словаря к нижнему регистру
                            iterable[internal.key] = {k.lower(): v for k, v in iterable[internal.key].items()}
                        else:
                            pass

    def payment_create(self, **kwargs):
        """Создание новой онлайн-оплаты.

        Args:
            event_uuid (uuid.UUID): Уникальный UUID события в БД.
            event_id (int): Идентификатор события в сервисе продажи билетов.
            order_uuid (uuid.UUID): Уникальный UUID заказа.
            order_id (int): Идентификатор заказа.
            customer (dict): Реквизиты покупателя.

                Содержимое ``customer``:
                    * name (str): ФИО.
                    * email (str): Электронная почта.
                    * phone (str): Телефон.

            overall (Decimal): Общая сумма заказа в рублях (**С возможными наценками или скидками**).

        Returns:
            dict: Параметры новой оплаты.

                Успешный ответ:
                    * success (bool): Запрос успешный (``True``).
                    * payment_id (str): Идентификатор оплаты.
                    * payment_url (str): URL платёжной формы.

                НЕуспешный ответ:
                    * success (bool): Запрос НЕуспешный (``False``).
                    * code (str): Код ошибки.
                    * message (str): Сообщение об ошибке.
        """
        method = 'POST'
        url = 'register.do'

        data = {}
        # Идентификатор заказа
        data['orderNumber'] = kwargs['order_id']
        # Полная сумма заказа с комиссией в копейках (целое число)
        data['amount'] = int(kwargs['overall'] * 100)
        # URL возврата после успешной оплаты
        data['returnUrl'] = '{url}?event_uuid={event_uuid}&order_uuid={order_uuid}'.format(
            url=str(self.__success_url),
            event_uuid=kwargs['event_uuid'],
            order_uuid=kwargs['order_uuid'],
        )
        # URL возврата после НЕуспешной оплаты
        data['failUrl'] = '{url}?event_uuid={event_uuid}&order_uuid={order_uuid}'.format(
            url=str(self.__error_url),
            event_uuid=kwargs['event_uuid'],
            order_uuid=kwargs['order_uuid'],
        )
        # Время на оплату заказа в секундах
        data['sessionTimeoutSecs'] = self.timeout * 60
        # Кастомные параметры заказа (можно отправлять любые данные)
        json_params = {}
        json_params['customer_name'] = kwargs['customer']['name']
        json_params['customer_email'] = kwargs['customer']['email']
        json_params['customer_phone'] = kwargs['customer']['phone']
        data['jsonParams'] = json.dumps(json_params, ensure_ascii=False).encode('utf-8')

        output_mapping = {
            # URL платёжной формы
            'formurl': self.internal('payment_url', str,),
            # Идентификатор оплаты
            'orderid': self.internal('payment_id', str,),
        }

        create = self.request(method, url, data, output_mapping)

        create['success'] = True if 'payment_url' in create else False

        if not create['success']:
            create['code'] = create.pop('errorcode')
            create['message'] = create.pop('errormessage')

        return create

    def payment_status(self, **kwargs):
        """Статус ранее созданной оплаты.

        Args:
            payment_id (str): Идентификатор оплаты.

        Returns:
            dict: Информация о статусе оплаты.
        """
        if not kwargs['payment_id']:
            response = {}
            response['success'] = False
            response['message'] = 'Отсутствует идентификатор онлайн-оплаты'
            return response

        method = 'POST'
        url = 'getOrderStatusExtended.do'
        data = {}
        # Идентификатор оплаты
        data['orderId'] = kwargs['payment_id']
        output_mapping = {
            'ordernumber':           self.internal('order_id', int,),
            'merchantorderparams':   self.internal('order_params', list,),
            'orderstatus':           self.internal('payment_code', int,),
            'attributes':            self.internal('payment_attributes', list,),
            'paymentamountinfo':     self.internal('payment_info', dict,),

            'actioncode':            self.internal('action_code', int,),
            'actioncodedescription': self.internal('action_message', str, 'OK'),

            'errorcode':             self.internal('code', int,),
            'errormessage':          self.internal('message', str, 'OK'),

            'amount':           None,
            'authdatetime':     None,
            'authrefnum':       None,
            'bankinfo':         None,
            'cardauthinfo':     None,
            'currency':         None,
            'date':             None,
            'ip':               None,
            'orderdescription': None,
            'terminalid':       None,
        }
        status = self.request(method, url, data, output_mapping)

        response = {}

        if status['success']:
            # Идентификатор заказа
            response['order_id'] = status['order_id']
            # Идентификатор оплаты (может ли его расположение в списке словарей меняться ???)
            response['payment_id'] = status['payment_attributes'][0]['value']
            # Общая сумма заказа в рублях (С комиссией)
            status['overall'] = response['overall'] = self.decimal_price(status['payment_info']['approvedamount'] / 100)
            # Сообщение о статусе оплаты
            # response['payment_message'] = status['payment_info']['paymentstate']

            # Был ли платёж возвращён
            response['is_refunded'] = True if status['payment_code'] == 4 else False

            # Результат успешен, только если платёж был успешно завершён
            if (
                # Код успешного завершения операции
                status['action_code'] == 0 and
                # Код успешного завершения оплаты или возврата
                (status['payment_code'] == 2 or status['payment_code'] == 4) and
                # Ненулевая сумма оплаты
                status['overall'] > 0
            ):
                response['success'] = True
            else:
                response['success'] = False

                response['code'] = status['action_code']
                response['message'] = status['action_message']

        del status

        return response

    def payment_refund(self, **kwargs):
        """Возврат суммы по ранее успешно завершённой оплате.

        Args:
            payment_id (str): Идентификатор оплаты.
            amount (Decimal): Сумма возврата в рублях.

        Returns:
            dict: Информация о возврате.

                Успешный ответ:
                    * success (bool): Запрос успешный (``True``).

                НЕуспешный ответ:
                    * success (bool): Запрос НЕуспешный (``False``).
                    * code (str): Код ошибки.
                    * message (str): Сообщение об ошибке.
        """
        if not kwargs['payment_id']:
            response = {}
            response['success'] = False
            response['message'] = 'Отсутствует идентификатор онлайн-оплаты'
            return response

        method = 'POST'
        url = 'refund.do'

        data = {}
        # Идентификатор оплаты
        data['orderId'] = kwargs['payment_id']
        # Полная сумма заказа с комиссией в копейках (целое число)
        data['amount'] = int(kwargs['amount']) * 100

        output_mapping = {
            'errorcode':    self.internal('action_code', int,),
            'errormessage': self.internal('action_message', str, 'OK'),
        }

        refund = self.request(method, url, data, output_mapping)
        # print('refund:', refund)

        # Успешный возврат
        # {'success': True, 'action_code': 0, 'action_message': 'Успешно'}

        # НЕуспешный возврат
        # {'success': False, 'action_code': 7, 'action_message': 'Платёж должен быть в корректном состоянии'}

        response = {}

        # Результат успешен, только если платёж был успешно возвращён
        if (
            # Успешный результат операции
            refund['success'] and
            # Код успешного завершения операции
            refund['action_code'] == 0
        ):
            response['success'] = True
            response['amount'] = kwargs['amount']
        else:
            response['success'] = False

            response['code'] = refund['action_code']
            response['message'] = refund['action_message']

        return response
