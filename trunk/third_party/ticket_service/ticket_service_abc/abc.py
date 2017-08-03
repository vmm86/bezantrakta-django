from abc import ABC, abstractmethod, abstractproperty


class TicketService(ABC):
    """
    Абстрактный класс-родитель конкретных классов любой системы продажи билетов.
    """
    def __init__(self):
        super().__init__()

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def version(self):
        pass

    # @abstractmethod
    # def discover_venues(self):
    #     pass

    # @abstractmethod
    # def discover_groups(self):
    #     pass

    # @abstractmethod
    # def discover_events(self):
    #     pass

    # @abstractmethod
    # def reserve(self, **kwargs):
    #     pass

    # @abstractmethod
    # def order_create(self):
    #     pass

    # @abstractmethod
    # def order_delete(self):
    #     pass

    # @abstractmethod
    # def order_approve(self):
    #     pass

    # @abstractmethod
    # def order_refund(self):
    #     pass
