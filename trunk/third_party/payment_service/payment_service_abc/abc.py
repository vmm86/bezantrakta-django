from abc import ABC, abstractmethod, abstractproperty
from collections import namedtuple
from decimal import Decimal


class PaymentService(ABC):
    """Абстрактный класс-родитель конкретных классов любой системы онлайн-оплаты.

    Перечисленные в этом классе абстрактные методы обязательно должны:

    * реализовываться в каждом дочернем классе;

    * возвращать одинаковые структуры данных (в том числе с одинаковыми ключами, содержащими одинаковые типы данных).
    """
    # Общие параметры, лежащие вне словаря ``init`` и помещающиеся в него для инстацирования класса
    GENERAL_PARAMS = ('commission', 'timeout',)

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

        Комиссия сервиса онлайн-оплаты добавляется к сумме заказа, если она не равна 0.
        Если комиссия равна ``0``, т.е. не используется, мы получаем ту же самую сумму.

        Args:
            total (Decimal): Сумма цен на билеты в заказе.

        Returns:
            Decimal: Общая сумма заказа.
        """
        return self.decimal_price(total + ((total * self.commission) / self.decimal_price(100)))

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
            event_uuid (uuid.UUID): Уникальный UUID события в БД.
            event_id (int): Идентификатор события в сервисе продажи билетов.
            order_uuid (uuid.UUID): Уникальный UUID заказа.
            order_id (int): Идентификатор заказа.
            overall (Decimal): Общая сумма заказа в рублях (**С возможными наценками или скидками**).
            customer (dict): Реквизиты покупателя.
                Содержимое ``customer``:
                    * name (str): ФИО.
                    * email (str): Электронная почта.
                    * phone (str): Телефон.

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
        pass

    @abstractmethod
    def payment_status(self, **kwargs):
        """Статус ранее созданной оплаты.

        Args:
            payment_id (str): Идентификатор оплаты.

        Returns:
            dict: Информация о статусе оплаты.
                Успешный ответ:
                    * success (bool): Запрос успешный (``True``).
                    * order_id (int): Идентификатор заказа.
                    * payment_id (str): Идентификатор оплаты.
                    * overall (Decimal): Общая сумма заказа в рублях (**С возможными наценками или скидками**).
                    * is_refunded (bool): Был ли проведён возврат суммы оплаты.
                НЕуспешный ответ:
                    * success (bool): Запрос НЕуспешный (``False``).
                    * code (str): Код ошибки.
                    * message (str): Сообщение об ошибке.
        """
        pass

    @abstractmethod
    def payment_refund(self, **kwargs):
        """Возврат суммы по ранее успешно завершённой оплате.

        Может не требоваться для работы по API и проводиться вручную в личном кабинете сервиса онлайн-оплаты.
        Используется, если необходимо отметить возврат синхронно И в сервисе продажи билетов, И в сервисе онлайн-оплаты.

        Args:
            order_id (int): Идентификатор заказа.
            payment_id (str): Идентификатор оплаты.
            amount (Decimal): Сумма возврата в рублях.
            reason (str): Причина возврата.

        Returns:
            dict: Информация о возврате.
                Успешный ответ:
                    * success (bool): Запрос успешный (``True``).
                НЕуспешный ответ:
                    * success (bool): Запрос НЕуспешный (``False``).
                    * code (str): Код ошибки.
                    * message (str): Сообщение об ошибке.
        """
        pass
