from .sberbank.api import Sberbank
from .sngb.api import SurgutNefteGazBank


PAYMENT_SERVICES = (Sberbank, SurgutNefteGazBank,)


def payment_service_factory(slug, init):
    """Фабрика для инстанцирования класса выбранного сервиса онлайн-оплаты.

    Args:
        slug (str): Псевдоним сервиса онлайн-оплаты (хранится как атрибут его класса).
        init (dict): Параметры для подключения к конкретному сервису онлайн-оплаты.

    Returns:
        class: Экземпляр класса выбранного сервиса онлайн-оплаты.
    """
    for ps in PAYMENT_SERVICES:
        if ps.slug == slug:
            return ps(init)
