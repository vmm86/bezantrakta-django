import simplejson as json

from django.conf import settings

from project.cache import ProjectCache

from ..models import TicketService
from ..ticket_service_abc import ticket_service_factory


class TicketServiceCache(ProjectCache):
    entities = ('ticket_service', )

    def get_model_object(self, object_id, **kwargs):
        return TicketService.objects.select_related(
                'domain',
            ).values(
                'id',
                'title',
                'slug',
                'is_active',
                'settings',
                'domain_id',
            ).get(
                id=object_id,
            )

    def cache_preprocessing(self, **kwargs):
        # Получение JSON-настроек сервиса продажи билетов
        self.value['settings'] = (
            json.loads(self.value['settings']) if self.value['settings'] is not None else None
        )

    def cache_postprocessing(self, **kwargs):
        # Проверка настроек, которые при отсутствии значений выставляются по умолчанию
        ticket_service_defaults = {
            # Максимальное число билетов в заказе
            'max_seats_per_order': settings.BEZANTRAKTA_DEFAULT_MAX_SEATS_PER_ORDER,
            # Таймаут для повторения запроса списка мест в событии в секундах
            'heartbeat_timeout': settings.BEZANTRAKTA_DEFAULT_HEARTBEAT_TIMEOUT,
            # Таймаут для выделения места в минутах, по истечении которого место автоматически освобождается
            'seat_timeout': settings.BEZANTRAKTA_DEFAULT_SEAT_TIMEOUT,
        }
        for par, val in ticket_service_defaults.items():
            if par not in self.value['settings'] or self.value['settings'][par] is None:
                self.value['settings'][par] = val

        # Получение экземпляра класса сервиса продажи билетов с использованием параметров из его ранее полученного кэша
        self.value['instance'] = ticket_service_factory(
            self.value['slug'],
            self.value['settings']['init'],
        )
