import simplejson as json

from django.db.models import F, Q

from third_party.ticket_service.models import TicketServiceDomainBinder
from third_party.ticket_service.models import TicketServiceVenueBinder
from third_party.ticket_service.ticket_service_abc import ticket_service_factory


def discover():
    """
    Поиск актуальных залов, событий, групп событий в подключенных к сайтам билетных сервисах.
    Запись полученной информации в соответствующие таблицы базы данных.
    """
    pass
