from django.conf import settings
from django.db.models import CharField, Case, When, Value, Q
from django.http.request import split_domain_port
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

from .models import City, Domain


class CurrentLocationMiddleware(MiddlewareMixin):
    """
    Получение информации о текущем городе и домене и её добавление в request.
    """
    def process_request(self, request):
        host = request.get_host()
        url_domain, url_port = split_domain_port(host)
        root_domain = settings.ROOT_DOMAIN
        root_domain_slug = settings.ROOT_DOMAIN_SLUG
        # Если URL содержит основной домен, указанный в настройках, вытаскиваем его поддомен(ы)
        if url_domain.endswith(root_domain):
            domain_slug = url_domain[:-len(root_domain)].rstrip('.')
            # Обход отсутствия поддомена для воронежского сайта
            domain_slug = root_domain_slug if domain_slug == '' else domain_slug

        request.domain_is_published = False

        # Получение информации о текущем домене в БД
        try:
            domain = Domain.objects.select_related('city').values(
                'id',
                'slug',
                'is_published',
                'city__title',
                'city__slug',
                'city__state'
            ).get(slug=domain_slug)
        # Если домен НЕ добавлен в БД - такой сайт не существует (ошибка 500)
        except Domain.DoesNotExist:
            context = {
                'title': """Сайт не существует""",
                'message': """<p>К сожалению, такого сайта у нас пока нет. 🙁</p>""",
            }
            return render(request, 'empty.html', context, status=500)
        # Если домен добавлен в БД
        else:
            request.domain_slug = domain['slug']
            request.domain_id = domain['id']
            request.domain_is_published = domain['is_published']

            request.city_title = domain['city__title']
            request.city_slug = domain['city__slug']
            request.city_state = domain['city__state']

            # Если город отключен - такой город не существует (ошибка 500)
            if request.city_state is False:
                context = {
                    'title': """Город не доступен""",
                    'message': """<p>К сожалению, этот город не доступен для посещения.</p>""",
                }
                return render(request, 'empty.html', context, status=500)
            # Если город в процессе подготовки - "скоро открытие" (ошибка 503)
            elif request.city_state is None:
                context = {
                    'title': """Скоро открытие""",
                    'message': """<p>Этот город пока в процессе подготовки, скоро открытие.</p>""",
                }
                return render(request, 'empty.html', context, status=503)
            # Если город включен
            elif request.city_state is True:
                # Если домен не опубликован - сайт недоступен (ошибка 503)
                if not request.domain_is_published:
                    context = {
                        'title': """Сайт на данный момент недоступен""",
                        'message': """<p>К сожалению, сайт временно недоступен.</p>
                        <p>Проводятся технические работы.</p>""",
                    }
                    return render(request, 'empty.html', context, status=503)
                # Если и город, и домен опубликованы
                else:
                    # Полный URL без опциональных GET-параметров (query string)
                    path = request.get_full_path().split('?')[0]

                    request.root_domain = settings.ROOT_DOMAIN
                    request.url_path = path
                    request.url_full = ''.join((url_domain, path,))

                # Получение списка городов для выбора
                try:
                    cities = City.objects.annotate(
                        status=Case(
                            When(state=True, then=Value('ready')),
                            default=Value('coming-soon'),
                            output_field=CharField()
                        ),
                    ).filter(
                        Q(state=True) | Q(state=None),
                    ).values(
                        'title',
                        'slug',
                        'state',
                        'status'
                    )
                except City.DoesNotExist:
                    context = {
                        'title': """Городов пока нет""",
                        'message': """<p>К сожалению, ни один город пока не доступен для показа. 🙁</p>""",
                    }
                    return render(request, 'empty.html', context, status=500)
                else:
                    request.cities = cities
                    # Псевдоним города из куки `bezantrakta_city`
                    request.bezantrakta_city = request.COOKIES.get('bezantrakta_city', None)

                # Получение из JSON настроек, специфичных для каждого домена
                import json
                import os

                try:
                    domain_settings_file = os.path.join(
                        settings.BASE_DIR,
                        'bezantrakta',
                        'location',
                        'domain_settings',
                        ''.join((request.domain_slug, '.json',))
                    )
                    with open(domain_settings_file) as dsf:
                        domain_settings = json.load(dsf)
                except FileNotFoundError:
                    pass
                else:
                    request.settings = domain_settings
