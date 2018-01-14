import pytz
import simplejson as json

from django.db.models import F

from project.cache import ProjectCache
from project.shortcuts import build_absolute_url

from ..models import Domain


class DomainCache(ProjectCache):
    entities = ('domain', )

    def get_model_object(self, object_id, **kwargs):
        return Domain.objects.select_related('city').annotate(
                domain_id=F('id'),
                domain_title=F('title'),
                domain_slug=F('slug'),
                domain_is_published=F('is_published'),
                domain_settings=F('settings'),

                city_title=F('city__title'),
                city_slug=F('city__slug'),
                city_timezone=F('city__timezone'),
                city_state=F('city__state'),
            ).values(
                'domain_id',
                'domain_title',
                'domain_slug',
                'domain_is_published',
                'domain_settings',

                'city_id',
                'city_title',
                'city_slug',
                'city_timezone',
                'city_state',
            ).get(domain_slug=object_id)

    def cache_preprocessing(self, **kwargs):
        # Получение настроек сайта
        self.value['domain_settings'] = (
            json.loads(self.value['domain_settings']) if self.value['domain_settings'] is not None else None
        )

    def cache_postprocessing(self, **kwargs):
        self.value['city_timezone'] = pytz.timezone(self.value['city_timezone'])

        # URL сайта (прокотол + домен) без слэша в конце (для подстановки к относительным ссылкам)
        self.value['url_protocol_domain'] = build_absolute_url(self.value['domain_slug'])
