import simplejson as json

from django.conf import settings

from project.cache import ProjectCache
from project.shortcuts import build_absolute_url

from ..models import PaymentService
from ..payment_service_abc import payment_service_factory
from ..payment_service_abc.abc import PaymentService as PaymentServiceABC


class PaymentServiceCache(ProjectCache):
    entities = ('payment_service', )

    def get_model_object(self, object_id, **kwargs):
        return PaymentService.objects.values(
                'id',
                'title',
                'slug',
                'is_active',
                'is_production',
                'settings'
            ).get(
                id=object_id,
            )

    def cache_preprocessing(self, **kwargs):
        # Получение настроек сервиса онлайн-оплаты
        self.value['settings'] = (
            json.loads(self.value['settings']) if self.value['settings'] is not None else None
        )

        # Тип оплаты помещается в `init` в виде строки 'test' или 'prod',
        # чтобы затем использоваться при инстанцировании класса
        self.value['settings']['init']['mode'] = 'prod' if self.value['is_production'] else 'test'

        # Общие параметры, лежащие вне `init`, помещаются в него,
        # чтобы затем использоваться при инстанцировании класса
        for gp in PaymentServiceABC.GENERAL_PARAMS:
            self.value['settings']['init'][gp] = self.value['settings'][gp]

    def cache_postprocessing(self, **kwargs):
        # URL для завершения заказа после удачной или НЕудачной оплаты
        domain_slug = (
            kwargs['domain_slug'] if
            'domain_slug' in kwargs and kwargs['domain_slug'] is not None else
            settings.BEZANTRAKTA_ROOT_DOMAIN_SLUG
        )
        self.value['settings']['init']['success_url'] = build_absolute_url(domain_slug, '/api/ps/success/')
        self.value['settings']['init']['error_url'] = build_absolute_url(domain_slug, '/api/ps/error/')

        # Получение экземпляра класса сервиса онлайн-оплаты с использованием параметров из его ранее полученного кэша
        self.value['instance'] = payment_service_factory(
            self.value['slug'],
            self.value['settings']['init'],
        )

        # Описание процесса онлайн-оплаты из атрибута класса онлайн-оплаты
        self.value['settings']['description'] = self.value['instance'].description
