from abc import ABC, abstractmethod, abstractproperty


class PaymentService(ABC):
    """
    Абстрактный класс-родитель конкретных классов любой системы онлайн-оплатыы.
    """
    def __init__(self):
        super().__init__()

    def __str__(self):
        return self.__class__.__name__

    # @abstractmethod
    # def version(self):
    #     pass
