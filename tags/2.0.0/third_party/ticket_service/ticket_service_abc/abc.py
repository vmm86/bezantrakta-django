from collections import namedtuple
from decimal import Decimal

from abc import ABC, abstractmethod, abstractproperty


class TicketService(ABC):
    """Абстрактный класс-родитель конкретных классов любой системы продажи билетов.

    Перечисленные в этом классе абстрактные методы обязательно должны:
    * реализовываться в каждом дочернем классе;
    * возвращать одинаковые структуры данных (в том числе с одинаковыми ключами, содержащими одинаковые типы данных).
    """
    # Значения, которые можно приводить к булеву типу данных (например, в ответе запроса к API)
    BOOLEAN_VALUES = ['True', 'true', 1, '1', 'y', 'yes', 'д', 'да', ]

    # Фабрика для создания выходных параметров в ответах методов API
    internal = namedtuple('InternalParameter', 'key type default_value')
    internal.__new__.__defaults__ = (None,) * len(internal._fields)

    def __init__(self):
        """Конструктор класса."""
        super().__init__()

    def __str__(self):
        return self.__class__.__name__

    def decimal_price(self, value):
        """Преобразование входного значения в денежную сумму с 2 знаками после запятой (копейки) типа Decimal.

        Args:
            value (str): Входное значение (в любом случае строка - для обхода проблем с округлением float).

        Returns:
            Decimal: Денежная сумма.
        """
        return Decimal(str(value)).quantize(Decimal('0.00'))

    @abstractmethod
    def version(self):
        """Версия API сервиса продажи билетов.

        Returns:
            str: Версия API.
        """
        pass

    @abstractmethod
    def discover_venues(self):
        """Получение списка залов для записи в БД.

        Returns:
            list: Список словарей с информацией о зале.
                venue_id (int):    Идентификатор зала.
                venue_title (str): Название зала.
        """
        pass

    @abstractmethod
    def discover_groups(self):
        """Получение списка групп событий для записи в БД.

        Returns:
            list: Список словарей с информацией о группах событий.
                group_id (int):            Идентификатор группы событий.
                group_title (str):         Название группы событий.
                group_datetime (datetime): Дата и время группы событий (из самого раннего события в группе).
                group_text (str):          Описание группы событий (из самого раннего события в группе).
                group_min_price (Decimal): Минимальная цена билета группы событий  (из самого раннего события в группе).
                venue_id (int):            Идентификатор зала.
        """
        pass

    @abstractmethod
    def discover_events(self):
        """Получение списка событий для записи в БД.

        Returns:
            list: Список словарей с информацией о событиях.
                event_id (int):            Идентификатор события.
                event_title (str):         Название события.
                event_datetime (datetime): Дата и время события.
                event_text (str):          Описание события.
                event_min_price (Decimal): Минимальная цена билета в событии.
                event_min_age (int):       Ограничение по возрасту (по умолчанию 0).
                group_id (int):            Идентификатор группы событий.
                venue_id (int):            Идентификатор зала.
        """
        pass

    @abstractmethod
    def prices(self):
        """Список цен на билеты для легенды схемы зала, упорядоченный по возрастанию.

        Returns:
            list: Список цен (Decimal) по возрастанию.
        """
        pass

    @abstractmethod
    def seats(self):
        """Доступные для продажи места в конкретном событии, упорядоченнве по цене, сектору, ряду, месту.

        Args:
            ticket_service_id (str): Идентификатор сервиса продажи билетов.
            event_id (int): Идентификатор события.
            venue_id (int): Идентификатор зала.

        Returns:
            list: Список словарей с информацией о доступных к заказу местах.
                sector_id (int): Идентификатор сектора.
                sector_title (str): Название сектора (может браться из названия группы цен).
                row_id (int): Идентификатор ряда.
                seat_id (int): Идентификатор места.
                seat_title (str): Название места (может совпадать с идентификатором места).
                price (Decimal): Цена.
                price_order: Порядковый номер цены в списке цен события prices по возрастанию.
                price_group_id (int): Идентификатор группы цен (только Радарио).
        """
        pass

    @abstractmethod
    def reserve(self, **kwargs):
        """Добавление или удаление места в предварительном резерве мест (корзина заказа).

        Метод возвращает передаваемые ему аргументы с подтверждением успешного или НЕуспешного результата.

        Резерв обязательно хранится на клиентской стороне в cookie.
        В зависимости от сервиса продажи билетов он одновременно может формироваться и на его сервере (СуперБилет).

        Args:
            ticket_service_id (str): Идентификатор сервиса продажи билетов.
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID заказа, а также номер сессии (только СуперБилет).
            action (str): Действие ('add' - добавить в резерв, 'remove' - удалить из резерва).
            sector_id (int): Идентификатор сектора (только СуперБилет).
            sector_title (str): Название сектора.
            row_id (int): Идентификатор ряда (только СуперБилет).
            seat_id (int): Идентификатор места.
            seat_title (str): Название места.
            price_group_id (int): Идентификатор группы цен (только Радарио).

        Returns:
            dict: Атрибуты места (входные аргументы) с подтверждением успешного или НЕуспешного резерва.
                success (bool): Успешный или НЕуспешный результат.
        """
        pass

    @abstractmethod
    def ticket_status(self, **kwargs):
        """Проверка состояния места (перед созданием заказа или перед онлайн-оплатой) (только СуперБилет).

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
        pass

    @abstractmethod
    def order_create(self, **kwargs):
        """Создание заказа из предварительно зарезервированных мест.

        Args:
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID заказа (на данный момент генерируется на клиенте).
            customer (dict): Реквизиты покупателя.
            customer[name] (str): ФИО покупателя.
            customer[email] (str): Электронная почта покупателя.
            customer[phone] (str): Телефон покупателя.
            customer[is_courier] (bool): Нужна ли доставка или нет.
            customer[address] (str): Адрес доставки (если она нужна).
            tickets (list): Список словарей с параметрами заказываемых билетов.
            tickets[sector_id] (int): Идентификатор сектора.
            tickets[row_id] (int): Идентификатор ряда.
            tickets[seat_id] (int): Идентификатор места.

        Returns:
            list: Список словарей с информацией о билетах в заказе.
            order_id (int): Идентификатор заказа в сервисе заказа билетов.
            tickets (list): Информация о заказанных билетах.
            tickets[ticket_uuid] (str): Уникальный UUID билета (на данный момент генерируется на клиенте).
            tickets[bar_code] (str): Штрих-код билета (СуперБилет - 20 символов, Радарио - 12 символов).
        """
        pass

    @abstractmethod
    def order_delete(self, **kwargs):
        """Удаление заказа.

        Args:
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID заказа.
            order_id (int): Идентификатор заказа.
            tickets (list): Список словарей с параметрами заказываемого места.
                sector_id (int): Идентификатор сектора.
                row_id (int): Идентификатор ряда.
                seat_id (int): Идентификатор места.

        Returns:
            dict: Информация об удалении заказа.
                success (bool): Успешное или НЕуспешное удаление заказа.
        """
        pass

    @abstractmethod
    def order_payment(self, **kwargs):
        """Отметка об оплате созданного ранее заказа.

        Args:
            event_id (int): Идентификатор события.
            order_uuid (str): Уникальный UUID заказа.
            order_id (int): Идентификатор заказа (только Радарио).
            payment_id (int): Идентификатор оплаты.
            payment_datetime(datetime): Дата и время оплаты.
            tickets (list): Список словарей с параметрами заказываемого места.
                sector_id (int): Идентификатор сектора.
                row_id (int): Идентификатор ряда.
                seat_id (int): Идентификатор места.

        Returns:
            dict: Информация об успешной или НЕуспешной оплате.
                success (bool): Успешное или НЕуспешное удаление заказа.
        """
        pass

    # @abstractmethod
    # def order_refund(self, **kwargs):
    #     pass
