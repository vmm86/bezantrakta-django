# import logging
import simplejson as json

from django.core.cache import cache

from third_party.ticket_service.models import TicketService
from third_party.ticket_service.ticket_service_abc import ticket_service_factory


def get_or_set_cache(ticket_service_id, reset=False):
    """Кэширование параметров сервиса продажи билетов для последующего использования без запросов в БД.

    Args:
        ticket_service_id (str): ID сервиса продажи билетов в БД.
        reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.

    Returns:
        cache: Кэш параметров сервиса продажи билетов.
    """
    # logger = logging.getLogger('bezantrakta.default')

    cache_key = 'ticket_service.{ticket_service_id}'.format(ticket_service_id=ticket_service_id)
    cache_value = cache.get(cache_key)

    # logger.info('\nИсходный кэш:\n{}'.format(cache_value['settings']['order_description']['email_online']))

    if reset:
        cache.delete(cache_key)
        # logger.info('\nПринудительное удаление (reset)')

    if not cache_value or reset:
        ts = dict(TicketService.objects.select_related(
            'domain',
        ).values(
            'id',
            'title',
            'slug',
            'is_active',
            'settings',
            'domain_id',
        ).get(
            id=ticket_service_id,
        ))

        # Получение настроек сервиса продажи билетов
        ts['settings'] = (
            json.loads(ts['settings']) if ts['settings'] is not None else None
        )

        cache_value = {k: v for k, v in ts.items()}
        # logger.info('\nНовый кэш:\n{}'.format(cache_value['settings']['order_description']['email_online']))
        cache.set(cache_key, json.dumps(cache_value, ensure_ascii=False))
        # logger.info('\nПерезапись кэша')
    else:
        cache_value = json.loads(cache.get(cache_key))
        # logger.info('\nИмеющийся кэш без перезаписи:\n{}'.format(cache_value['settings']['order_description']['email_online']))

    return cache_value


def ticket_service_instance(ticket_service_id):
    """Получение экземпляра класса сервиса продажи билетов с использованием параметров из его кэша.

    Args:
        ticket_service_id (str): ID сервиса продажи билетов в БД.

    Returns:
        TicketService: Экземпляр класса конкретного сервиса продажи билетов.
    """
    cache_key = 'ticket_service.{ticket_service_id}'.format(ticket_service_id=ticket_service_id)
    cache_value = json.loads(cache.get(cache_key))

    # Экземпляр класса сервиса продажи билетов
    ts = ticket_service_factory(
        cache_value['slug'],
        cache_value['settings']['init'],
    )

    return ts