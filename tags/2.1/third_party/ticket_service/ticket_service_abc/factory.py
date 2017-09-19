from .radario.api import Radario
from .superbilet.api import SuperBilet


TICKET_SERVICES = [SuperBilet, Radario, ]


def ticket_service_factory(slug, init):
    """Фабрика для инстанцирования класса выбранного сервиса продажи билетов.

    Args:
        slug (str): Псевдоним сервиса продажи билетов (хранится как атрибут его класса).
        init (dict): Параметры для подключения к конкретному сервису продажи билетов.

    Returns:
        class: Экземпляр класса выбранного сервиса продажи билетов.
    """
    for ts in TICKET_SERVICES:
        if ts.slug == slug:
            return ts(init)
