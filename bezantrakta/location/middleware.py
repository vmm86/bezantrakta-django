from django.conf import settings
from django.http.request import split_domain_port
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


from .models import Domain


class CurrentDomainMiddleware(MiddlewareMixin):
    """
    Получение информации о текущем домене и её добавление в request.
    """
    def process_request(self, request):
        host = request.get_host()
        url_domain, url_port = split_domain_port(host)
        # Если URL содержит основной домен, указанный в настройках, вытаскиваем его поддомен(ы)
        if url_domain.endswith(settings.ROOT_DOMAIN):
            domain_slug = url_domain[:-len(settings.ROOT_DOMAIN)].rstrip('.')
            # Обход отсутствия поддомена для воронежского сайта
            domain_slug = settings.ROOT_DOMAIN_SLUG if domain_slug == '' else domain_slug

        request.domain_is_published = False

        # Получение информации о текущем домене в БД
        try:
            domain = Domain.objects.select_related('city').values(
                'id',
                'slug',
                'is_published',
                'city__title',
                'city__slug',
                'city__is_published'
            ).get(slug=domain_slug)
        # Если домен НЕ добавлен в БД - такой сайт не существует (ошибка 500)
        except Domain.DoesNotExist:
            context = {
                'title': """Сайт не существует""",
                'message': """<p>К сожалению, такого сайта у нас пока нет. 🙁</p>
                <p>👉 Выберите интересущий Вас город из списка.</p>""",
            }
            return render(request, 'empty.html', context, status=500)
        # Если домен добавлен в БД
        else:
            request.city_title = domain['city__title']
            request.city_slug = domain['city__slug']
            request.city_is_published = domain['city__is_published']

            request.domain_slug = domain['slug']
            request.domain_id = domain['id']
            request.domain_is_published = domain['is_published']

            # Если город не опубликован - "скоро открытие" (ошибка 503)
            if not request.city_is_published:
                context = {
                    'title': """Скоро открытие""",
                    'message': """<p>Этот сайты ещё не доступен для посещения, скоро открытие.</p>
                    <p>👉 Выберите интересущий Вас город из списка.</p>""",
                }
                return render(request, 'empty.html', context, status=503)
            # Если домен не опубликован - сайт недоступен (ошибка 503)
            elif not request.domain_is_published:
                context = {
                    'title': """Сайт на данный момент недоступен""",
                    'message': """<p>К сожалению, сайт временно недоступен.</p>
                    <p>Проводятся технические работы.</p>
                    <p>👉 Заходите к нам позднее.</p>""",
                }
                return render(request, 'empty.html', context, status=503)
            # Если и город, и домен опубликованы
            else:
                full_path = request.get_full_path()
                # Path without optional query string
                path = full_path.split('?')[0]
                request.url_path = path
                request.url_full = ''.join((url_domain, path,))

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
