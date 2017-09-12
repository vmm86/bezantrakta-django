from abc import ABC, abstractmethod, abstractproperty
from collections import namedtuple
from decimal import Decimal


class PaymentService(ABC):
    """Абстрактный класс-родитель конкретных классов любой системы онлайн-оплаты.

    Перечисленные в этом классе абстрактные методы обязательно должны:

    * реализовываться в каждом дочернем классе;

    * возвращать одинаковые структуры данных (в том числе с одинаковыми ключами, содержащими одинаковые типы данных).
    """
    # Значения, которые можно приводить к булеву типу данных (например, в ответе запроса к API)
    BOOLEAN_VALUES = ('True', 'true', 1, '1', 'y', 'yes', 'д', 'да',)

    # Общие параметры, лежащие вне словаря ``init`` и помещающиеся в него для инстацирования класса
    GENERAL_PARAMS = ('commission', 'commission_included', 'timeout',)

    # Фабрика для создания выходных параметров в ответах методов API
    internal = namedtuple('InternalParameter', 'key type default')
    internal.__new__.__defaults__ = (None,) * len(internal._fields)

    def __init__(self):
        """Конструктор класса."""
        super().__init__()

    def __str__(self):
        return self.__class__.__name__

    def version(self):
        """Версия API сервиса продажи билетов.

        Returns:
            str: Версия API.
        """
        pass

    def decimal_price(self, value):
        """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа ``Decimal``.

        Args:
            value (str): Входное значение (в любом случае строка - для обхода проблем с округлением ``float``).

        Returns:
            Decimal: Денежная сумма.
        """
        return Decimal(str(value)).quantize(Decimal('1.00'))

    def commission(self):
        """Процент комиссии.

        Returns:
            Decimal: Процент комиссии.
        """
        return self.commission

    def total_plus_commission(self, total):
        """Общая сумма заказа при онлайн-оплате.

        Комиссия сервиса онлайн-оплаты либо добавляется к сумме заказа, либо включается в неё.
        Если комиссия входит в сумму заказа, мы получаем ту же самую сумму.
        Если комиссия добавляется к сумме заказа, мы получаем сумму заказа с комиссией.

        При оформлении заказа:

        * получаем общую сумму заказа с учётом комиссии с помощью этого метода,

        * при оформлении записываем эту сумму в БД,

        * затем в других методах ``PaymentService`` используем полученную общую сумму заказа без доп. конвертации.

        Args:
            total (Decimal): Сумма заказа (**БЕЗ комиссии**).

        Returns:
            Decimal: Общая сумма заказа.
        """
        return (
            self.decimal_price(total) if
            self.commission_included else
            self.decimal_price(total + ((total * self.commission) / self.decimal_price(100)))
        )

    def description(self):
        """Описание процесса оплаты билетов.

        Returns:
            str: HTML-код описания.
        """
        return self.description

    def timeout(self):
        """Таймаут до завершения оплаты в минутах.

        Returns:
            int: Таймаут.
        """
        return self.timeout

    @abstractmethod
    def payment_create(self, **kwargs):
        """Создание новой онлайн-оплаты.

        Args:
            event_id (int): Идентификатор события.
            customer (dict): Реквизиты покупателя.

                Содержимое ``customer``:
                    * **name** (str): ФИО.
                    * **email** (str): Электронная почта.
                    * **phone** (str): Телефон.
            order (dict): Параметры заказа.

                Содержимое ``order``:
                    * **uuid** (str): Уникальный UUID заказа.
                    * **id** (int): Идентификатор заказа.
                    * **total** (Decimal): Общая сумма заказа в рублях (**С комиссией**).

        Returns:
            dict: Параметры новой оплаты.

            Успешный ответ:
                * **success** (bool): Запрос успешный (``True``).
                * **payment_id** (str): Идентификатор оплаты.
                * **payment_url** (str): URL платёжной формы.

            НЕуспешный ответ:
                * **success** (bool): Запрос НЕуспешный (``False``).
                * **code** (str): Код ошибки.
                * **message** (str): Сообщение об ошибке.
        """
        pass

    @abstractmethod
    def payment_status(self, **kwargs):
        """Статус ранее созданной оплаты.

        Args:
            payment_id (str): Идентификатор оплаты.

        Returns:
            dict: Информация о статусе оплаты.

            Успешный ответ:
                * **success** (bool): Запрос успешный (``True``).
                * **code** (str): Код ошибки (``0``).
                * **message** (str): Сообщение об ошибке (``OK``).
                * **order_id** (int): Идентификатор заказа.
                * **order_params** (list): Параметры заказа, отправленные при создании оплаты (список из словарей, каждый из которых содержит ключи ``name`` и ``value``).
                * **payment_id** (str): Идентификатор оплаты.
                * **total** (Decimal): Общая сумма заказа в рублях (**С комиссией**).
                * **is_refunded** (bool): Был ли проведён возврат суммы оплаты.

            НЕуспешный ответ:
                * **success** (bool): Запрос НЕуспешный (``False``).
                * **code** (str): Код ошибки.
                * **message** (str): Сообщение об ошибке.
        """
        pass

    @abstractmethod
    def payment_refund(self, **kwargs):
        """Возврат суммы по ранее успешно завершённой оплате.

        Может не требоваться для работы по API проводиться вручную в личном кабинете сервиса онлайн-оплаты.
        Выполняется, если необходимо отметить возврат синхронно и в сервисе продажи билетов, и в сервисе онлайн-оплаты.

        Args:
            payment_id (str): Идентификатор оплаты.
            total (Decimal): Общая сумма заказа в рублях (**С комиссией**).

        Returns:
            dict: Информация о возврате суммы заказа.

            Успешный ответ:
                * **success** (bool): Запрос успешный (``True``).
                * **code** (str): Код ошибки (``0``).
                * **message** (str): Сообщение об ошибке (``OK``).

            НЕуспешный ответ:
                * **success** (bool): Запрос НЕуспешный (``False``).
                * **code** (str): Код ошибки.
                * **message** (str): Сообщение об ошибке.
        """
        pass
