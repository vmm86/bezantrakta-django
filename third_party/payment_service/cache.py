import simplejson as json

from django.conf import settings
from django.core.cache import cache

from third_party.payment_service.models import PaymentService
from third_party.payment_service.payment_service_abc import payment_service_factory


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

        # Получение настроек сервиса онлайн-оплаты
        ps['settings'] = (
            json.loads(ps['settings']) if ps['settings'] is not None else None
        )

        # Тип оплаты кладётся в `init` в виде строки `test` или `prod`,
        # чтобы затем использоваться при инстацировании класса
        ps['settings']['init']['mode'] = 'prod' if ps['is_production'] else 'test'

        cache_value = {k: v for k, v in ps.items()}
        cache.set(cache_key, json.dumps(cache_value, ensure_ascii=False))
    else:
        cache_value = json.loads(cache.get(cache_key))

    # print(cache_key, ':\n', cache_value, '\n')

    return cache_value


def payment_service_instance(payment_service_id, url_domain=None):
    """Получение экземпляра класса сервиса продажи билетов с использованием параметров из его кэша.

    Args:
        payment_service_id (str): ID сервиса онлайн-оплаты в БД.
        url_domain (str, optional): Корневой домен текущего сайта для URL завершения удачной или НЕудачной оплаты.

    Returns:
        PaymentService: Экземпляр класса конкретного сервиса онлайн-оплаты.
    """
    cache_key = 'payment_service.{payment_service_id}'.format(payment_service_id=payment_service_id)
    cache_value = json.loads(cache.get(cache_key))

    url_domain = url_domain if url_domain is not None else settings.BEZANTRAKTA_ROOT_DOMAIN

    # URL для завершения заказа после удачной или НЕудачной оплаты
    cache_value['settings']['init']['success_url'] = 'http://{url_domain}/api/ps/success/'.format(url_domain=url_domain)
    cache_value['settings']['init']['error_url'] = 'http://{url_domain}/api/ps/error/'.format(url_domain=url_domain)

    # Экземпляр класса сервиса продажи билетов
    ps = payment_service_factory(
        cache_value['slug'],
        cache_value['settings']['init'],
    )

    return ps
