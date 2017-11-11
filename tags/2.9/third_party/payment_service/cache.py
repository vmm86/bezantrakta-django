import simplejson as json

from django.conf import settings
from django.core.cache import cache

from project.shortcuts import build_absolute_url

from third_party.payment_service.models import PaymentService
from third_party.payment_service.payment_service_abc import payment_service_factory
from third_party.payment_service.payment_service_abc.abc import PaymentService as PaymentServiceABC


def get_or_set_cache(payment_service_id, reset=False):
    """Кэширование параметров сервиса онлайн-оплаты для последующего использования без запросов в БД.

    Args:
        payment_service_id (str): ID сервиса онлайн-оплаты в БД.
        reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.

    Returns:
        cache: Кэш параметров сервиса онлайн-оплаты.
    """
    cache_key = 'payment_service.{payment_service_id}'.format(payment_service_id=payment_service_id)
    cache_value = cache.get(cache_key)

    if reset:
        cache.delete(cache_key)

    if not cache_value or reset:
        try:
            ps = dict(PaymentService.objects.values(
                'id',
                'title',
                'slug',
                'is_active',
                'is_production',
                'settings'
            ).get(
                id=payment_service_id,
            ))
        except PaymentService.DoesNotExist:
            return None
        else:
            # Получение настроек сервиса онлайн-оплаты
            ps['settings'] = (
                json.loads(ps['settings']) if ps['settings'] is not None else None
            )

            # Тип оплаты помещается в init в виде строки `test` или `prod`,
            # чтобы затем использоваться при инстанцировании класса
            ps['settings']['init']['mode'] = 'prod' if ps['is_production'] else 'test'

            # Общие параметры, лежащие вне init, помещаются в него,
            # чтобы затем использоваться при инстанцировании класса
            for gp in PaymentServiceABC.GENERAL_PARAMS:
                ps['settings']['init'][gp] = ps['settings'][gp]

            cache_value = {k: v for k, v in ps.items()}
            cache.set(cache_key, json.dumps(cache_value, ensure_ascii=False))
    else:
        cache_value = json.loads(cache.get(cache_key))

    return cache_value


def payment_service_instance(payment_service_id, domain_slug=None):
    """Получение экземпляра класса сервиса продажи билетов с использованием параметров из его кэша.

    Args:
        payment_service_id (str): ID сервиса онлайн-оплаты в БД.
        domain_slug (str, optional): Псевдоним (поддомен) текущего сайта для URL завершения онлайн-оплаты.

    Returns:
        PaymentService: Экземпляр класса конкретного сервиса онлайн-оплаты.
    """
    cache_key = 'payment_service.{payment_service_id}'.format(payment_service_id=payment_service_id)
    cache_value = json.loads(cache.get(cache_key))

    # URL для завершения заказа после удачной или НЕудачной оплаты
    domain_slug = domain_slug if domain_slug is not None else settings.BEZANTRAKTA_ROOT_DOMAIN_SLUG
    cache_value['settings']['init']['success_url'] = build_absolute_url(domain_slug, '/api/ps/success/')
    cache_value['settings']['init']['error_url'] = build_absolute_url(domain_slug, '/api/ps/error/')

    # Экземпляр класса сервиса продажи билетов
    ps = payment_service_factory(
        cache_value['slug'],
        cache_value['settings']['init'],
    )

    return ps
