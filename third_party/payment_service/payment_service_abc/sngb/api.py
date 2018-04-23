import hashlib
import requests
from urllib.parse import parse_qsl, urlsplit

from ..abc import PaymentService


class SurgutNefteGazBank(PaymentService):
    """Класс для работы с API СургутНефтеГазБанка.

    Любой метод, делающий запросы к API, вызывает для этого конструктор запросов ``request``.

    Атрибуты класса:
        slug (str): Псевдоним для инстанцирования класса (``sngb``).

    Attributes:
        commission (Decimal): Процент комиссии.
        timeout (int): Таймаут до завершения оплаты в минутах (по умолчанию - **15 минут**).
    """
    slug = 'sngb'

    # Базовый URL для отправки запросов к API тестовой или настоящей оплаты
    __TEST_HOST = 'https://ecm.sngb.ru:443/ECommerce'
    __PROD_HOST = 'https://ecm.sngb.ru:443/Gateway'

    # Коды транзакций
    PAYMENT_ACTIONS = {
        'PURCHASE':           1,  # покупка (авторизация + подтверждение)
        'CREDIT':             2,  # возврат платежа
        'AUTHORIZATION':      4,  # авторизация (проверка карты и доступности средств для покупки)
        'CAPTURE':            5,  # подтверждение (успешное завершение оплаты)
        'VOID_AUTHORIZATION': 9,  # отмена авторизации (сниятие блокировки средств на карте клиента)
        'VOID_CAPTURE':       7,  # отмена подтверждения
        'VOID_CREDIT':        6,  # отмена возврата платежа
    }

    # Сообщения о статусе оплаты в ответе self.payment_status
    PAYMENT_STATUS_MESSAGES = {
        'AUTHORIZATION': 'авторизация (проверка карты и доступности средств для покупки)',
        'CAPTURE':       'подтверждение (дальнейшая обработка оплаты)',
        'VOID':          'отмена оплаты',
        'CREDIT':        'возврат средств',
    }

    # Результаты операций
    PAYMENT_RESULT = {
        'CAPTURED':     'успешное подтверждение',
        'APPROVED':     'успешная авторизация',
        'VOIDED':       'успешная отмена',
        'NOT CAPTURED': 'подтверждение отклонено',
        'NOT APPROVED': 'авторизация отклонена',
        'NOT VOIDED':   'отмена отклонена',
        'CANCELED':     'клиент отменил операцию',
        'HOST TIMEOUT': 'хост не ответил в отведенное время',
    }

    # Код ответа авторизационной системы
    PAYMENT_RESPONSE_CODES = {
        '00': 'Транзакция прошла успешно',
        '04': 'Недействительный номер карты',
        '14': 'Неверный номер карты',
        '33': 'Истек срок действия карты',
        '54': 'Истек срок действия карты',
        'Q1': 'Неверный срок действия карты или карта просрочена',
        '51': 'Недостаточно средств',
        '56': 'Неверный номер карты',
    }

    def __init__(self, init):
        """Конструктор класса.

        Args:
            init (dict): Словарь с параметрами для инстанцирования класса.

                Содержимое ``init``:
                    * **mode** (str): Тестовая или настоящая оплата
                    * **test_merchant_id** (str): Идентификатор мерчанта для тестового доступа к API.
                    * **test_terminal_alias** (str): Алиас терминала для тестового доступа к API.
                    * **test_psk** (str): Cекретный ключ для тестового доступа к API.
                    * **test_token** (str): Токен для тестового доступа к API.
                    * **prod_merchant_id** (str): Идентификатор мерчанта для production-доступа к API.
                    * **prod_terminal_alias** (str): Алиас терминала для production-доступа к API.
                    * **prod_psk** (str): Cекретный ключ аутентификации запросов для production-доступа к API.
                    * **prod_token** (str): Токен для production-доступа к API.
                    * **success_url** (str): URL для обработки удачной оплаты.
                    * **error_url** (str): URL для обработки НЕудачной оплаты.
                    * **commission** (float): Комиссия (преобразуется в ``Decimal``).
                    * **timeout** (int): Время сессии на оплату в минутах (по умолчанию - **15 минут**).
        """
        super().__init__()

        # Параметры подключения
        self.__mode = init['mode']  # ('test', 'prod',)

        if self.__mode == 'test':
            self.__payment_type = 'ECommerce'
            self.__host = SurgutNefteGazBank.__TEST_HOST
            self.__merchant_id = init['test_merchant_id']
            self.__terminal_alias = init['test_terminal_alias']
            self.__psk = init['test_psk']
            self.__token = init['test_token']
        elif self.__mode == 'prod':
            self.__payment_type = 'Gateway'
            self.__host = SurgutNefteGazBank.__PROD_HOST
            self.__merchant_id = init['prod_merchant_id']
            self.__terminal_alias = init['prod_terminal_alias']
            self.__psk = init['prod_psk']
            self.__token = init['prod_token']

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
        <p>Оплата проводится с использованием услуг Интернет-эквайринга <strong>Акционерного общества «Сургутнефтегазбанк» (АО БАНК «СНГБ»)</strong> с использованием банковских карт платёжных систем:
        <ul>
            <li><img src="/media/global/banner/banner_payment/type-mir.png" width="43" height="25" style="vertical-align: middle;"> <strong>МИР</strong></li>
            <li><img src="/media/global/banner/banner_payment/type-visa.png" width="43" height="25" style="vertical-align: middle;"> <strong>VISA International</strong></li>
            <li><img src="/media/global/banner/banner_payment/type-mc.png" width="43" height="25" style="vertical-align: middle;"> <strong>MasterCard World Wide</strong></li>
            </li>
        </ul>
        </p>
        """

    def __str__(self):
        return '{cls}({user}: {mode})'.format(
            cls=self.__class__.__name__,
            user=self.__user,
            mode=self.__mode,
        )

    def request(self, method, url, data):
        """Конструктор запросов к API.

        Args:
            method (str): HTTP-метод (``GET`` или ``POST``).
            url (str): Относительный URL конкретного метода API.
            data (dict): Параметры запроса для GET или тело запроса для POST.
            test (bool, optional): Опциональный параметр для тестирования работы.

        Returns:
            list, dict: Обработанный ответ конкретного метода API.
        """
        if not url.startswith('http'):
            url = '{host}/{url}'.format(
                host=self.__host,
                url=url
            )

        # Секретный хэш для авторизации любых запросов
        if (data):
            secret_key = '{merchant_id}{overall}{order_id}{action}{psk}'.format(
                merchant_id=self.__merchant_id,
                overall=data['amt'],
                order_id=data['trackid'],
                action=data['action'],
                psk=self.__psk
            ).encode('utf-8')
            data['udf5'] = hashlib.sha1(secret_key).hexdigest()

        if method == 'GET':
            response = requests.get(url, params=data)
        elif method == 'POST':
            response = requests.post(url, data=data)

        # Пытаемся возвратить JSON-ответ либо обычный ответ
        try:
            return response.json()
        except ValueError:
            return response.text

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
        url = 'PaymentInitServlet'

        data = {}
        data['merchant'] = self.__merchant_id
        data['terminal'] = self.__terminal_alias
        data['action'] = SurgutNefteGazBank.PAYMENT_ACTIONS['PURCHASE']
        # Идентификатор заказа
        data['trackid'] = kwargs['order_id']
        # Полная сумма заказа
        data['amt'] = str(kwargs['overall'])
        # Кастомные параметры заказа (можно отправлять любые данные)
        # |-- Идентификатор события
        data['udf1'] = kwargs['event_id']
        # |-- Уникальный UUID события
        data['udf2'] = kwargs['event_uuid']
        # |-- Email покупателя
        data['udf3'] = kwargs['customer']['name']
        # |-- Уникальный UUID заказа
        data['udf4'] = str(kwargs.get('order_uuid', '-'))

        create = self.request(method, url, data).rstrip()

        # Успешный запрос новой оплаты
        # success_url: "https://ecm.sngb.ru:443/ECommerce/hppaction?formAction=com.aciworldwide.commerce.gateway.payment.action.HostedPaymentPageAction&PaymentID=6860031491873320\r\n"

        # НЕуспешный запрос новой оплаты
        # error_url: "http://MyOnlineShop/Error?error=CGW00001&errortext=ErrorDescription"

        response = {}

        if type(create) is str and not create.startswith('<!DOCTYPE'):
            # Разбираем URL в ответе, получаем идентификатор оплаты
            parsed_result = dict(parse_qsl(urlsplit(create).query))
            # print('parsed_result: ', parsed_result, '\n')

            # Если запрос успешен
            if 'PaymentID' in parsed_result:
                response['success'] = True
                response['payment_url'] = create
                response['payment_id'] = parsed_result['PaymentID']
            # Если запрос НЕуспешен
            else:
                response['success'] = False
                response['code'] = parsed_result['error']
                response['message'] = parsed_result['errortext']
        else:
            response['success'] = False

        return response

    def _transactions(self, payment_id):
        """Список транзакций по текущей оплате.

        Args:
            payment_id (str): Идентификатор оплаты.

        Returns:
            dict: Информация о транзакциях.
            """
        method = 'GET'
        url = 'https://{token}:@ecm.sngb.ru/{payment_type}/v1/transactions/{payment_id}'.format(
            token=self.__token,
            payment_type=self.__payment_type,
            payment_id=payment_id,
        )
        data = {}

        transactions = self.request(method, url, data)

        # print('transactions:', transactions)

        # {
        # 'tranlist': [
        #     {
        #         'result': 'APPROVED',
        #         'tranid': 6234585261980990,
        #         'track': '16180',
        #         'transdt': 1523284019093,
        #         'action': 'authorization',
        #         'amount': 10.18,
        #         'orderid': 6234585261980990
        #     },
        #     {
        #         'result': 'CAPTURED',
        #         'tranid': 3031783261980990,
        #         'track': '16180',
        #         'transdt': 1523284019093,
        #         'action': 'capture',
        #         'amount': 10.18,
        #         'orderid': 6234585261980990
        #     },
        # ], 'object': 'list'
        # }

        response = {}

        if not transactions or not transactions.get('tranlist'):
            response = {}
            response['success'] = False
            response['message'] = 'В указанной онлайн-оплате нет ни одной транзакции'
            return response
        else:
            response['success'] = True
            response['transactions'] = {}

        for tran in transactions['tranlist']:
            response['transactions'][tran['result']] = tran['tranid']

        return response

    def _payments(self, payment_id):
        """Информация об онлайн-оплате.

        Args:
            payment_id (str): Идентификатор оплаты.

        Returns:
            dict: Информация об онлайн-оплате.
        """
        method = 'GET'
        url = 'https://{token}:@ecm.sngb.ru/{payment_type}/v1/payments/{payment_id}'.format(
            token=self.__token,
            payment_type=self.__payment_type,
            payment_id=payment_id,
        )
        data = {}

        payments = self.request(method, url, data)

        # print('payments:', payments)

        # Успешная оплата
        # {
        #   'data': [{
        #     'authorization': true,
        #     'captured': true,
        #     'refunded': false,
        #     'created': 1512467655718,
        #     'tranid': '6443917541473390',
        #     'track': '12975',
        #     'id': 3199591541473390,
        #     'amount': 1.02,
        #     'currency': 'rub',
        #     'object': 'payment',
        #     'livemode': true,
        #   }],
        #   'count': '1',
        #   'url': '/ECommerce/v1/payments',
        #   'object': 'list',
        # }

        # НЕуспешная оплата
        # {
        # 'data': [{
        #     'authorization': false,
        #     'captured': false,
        #     'refunded': false,
        #     'created': 1512550283416,
        #     'tranid': '',
        #     'track': '13020',
        #     'id': 4769758511373400,
        #     'amount': 1.02,
        #     'currency': 'rub',
        #     'object': 'payment',
        #     'livemode': true,
        # }]
        # 'count': '1',
        # 'url': '/ECommerce/v1/payments',
        # 'object': 'list',
        # }

        # Отсутствие оплаты
        # {
        #   'data': [],
        #   'count': '0',
        #   'url': '/ECommerce/v1/payments',
        #   'object': 'list',
        # }

        response = {}

        # Если оплата существует
        if payments and payments['data']:
            # Идентификатор заказа
            response['order_id'] = int(payments['data'][0]['track'])
            # Идентификатор оплаты
            response['payment_id'] = payments['data'][0]['id']
            # Общая сумма заказа
            response['overall'] = self.decimal_price(payments['data'][0]['amount'])
            # Был ли платёж возвращён
            response['is_refunded'] = True if payments['data'][0]['refunded'] else False

            # Если оплата завершилась успешно
            if (
                payments['data'][0]['authorization'] and
                payments['data'][0]['captured']
            ):
                response['success'] = True
            # Если оплата завершилась НЕуспешно
            else:
                response['success'] = False

                response['code'] = 'ERROR'
                response['message'] = 'Оплата завершилась с ошибкой'
        # Если оплата НЕ существует
        else:
            response['success'] = False

            response['code'] = 'NONE'
            response['message'] = 'Запрошенная оплата не существует'

        return response

    def payment_status(self, **kwargs):
        """Статус ранее созданной оплаты (включая список транзакций).

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

        # Информация об онлайн-оплате
        payments = self._payments(kwargs['payment_id'])
        # Информация от транзакциях
        transactions = self._transactions(kwargs['payment_id'])

        response = {}

        if payments['success'] and transactions['success']:
            response['success'] = True

            # Идентификатор заказа
            response['order_id'] = payments['order_id']
            # Идентификатор оплаты
            response['payment_id'] = payments['payment_id']
            # Общая сумма заказа
            response['overall'] = payments['overall']
            # Был ли платёж возвращён
            response['is_refunded'] = payments['is_refunded']

            response['transactions'] = transactions['transactions']

        else:
            response['success'] = False
            response['message'] = 'Ошибка при запросе статуса онлайн-оплаты'

        return response

    def payment_refund(self, **kwargs):
        """Возврат суммы по ранее успешно завершённой оплате.

        Для получения ``transaction_id`` выполняется метод ``payment_status``.

        При попытке выполнить метод с вручную указанным ``transaction_id`` получаем ошибку *CGW000316 Batch Transaction Processing Not Enabled for Terminal*.

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

            amount (Decimal): Сумма возврата в рублях.
            payment_id (str): Идентификатор оплаты.

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

        # Статус оплаты
        payment_status = self.payment_status(payment_id=kwargs['payment_id'])
        if not payment_status['success']:
            response = {}
            response['success'] = False
            response['message'] = payment_status['message']
            return response

        method = 'POST'
        url = 'PaymentTranServlet'

        data = {}
        data['merchant'] = self.__merchant_id
        data['terminal'] = self.__terminal_alias
        data['action'] = SurgutNefteGazBank.PAYMENT_ACTIONS['CREDIT']
        data['amt'] = kwargs['amount']
        data['trackid'] = kwargs['order_id']
        data['paymentid'] = kwargs['payment_id']

        # Идентификатор транзакции 'CAPTURED', который нужно использовать для возврата
        data['tranid'] = payment_status['transactions']['CAPTURED']

        # Кастомные параметры заказа (можно отправлять любые данные)
        # |-- Идентификатор события
        data['udf1'] = kwargs['event_id'] if 'event_id' in kwargs else None
        # |-- Уникальный UUID события
        data['udf2'] = kwargs['event_uuid'] if 'event_uuid' in kwargs else None
        # |-- Email покупателя
        data['udf3'] = kwargs['customer']['name'] if 'customer' in kwargs else None
        # |-- Уникальный UUID заказа
        data['udf4'] = str(kwargs['order_uuid']) if 'order_uuid' in kwargs else None

        # Получение результата от промежуточного представления sngb_tran
        refund = self.request(method, url, data)
        # print('refund: ', refund, type(refund))

        return refund
