from django.conf import settings
from django.db.models import CharField, Case, When, Value, Q
from django.http.request import split_domain_port
from django.shortcuts import render
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from project.cache import cache_factory
from project.shortcuts import build_absolute_url, message, render_messages

from .models import City


class CurrentLocationMiddleware(MiddlewareMixin):
    """Получение информации о текущем городе и сайте и её добавление в ``request``."""
    def process_request(self, request):
        http_or_https = 'https://' if settings.BEZANTRAKTA_IS_SECURE else 'http://'
        host = request.get_host()
        url_domain, url_port = split_domain_port(host)
        root_domain = settings.BEZANTRAKTA_ROOT_DOMAIN
        root_domain_slug = settings.BEZANTRAKTA_ROOT_DOMAIN_SLUG
        # Если URL содержит основной домен, указанный в настройках, получаем его поддомен
        if url_domain.endswith(root_domain):
            domain_slug = url_domain[:-len(root_domain)].rstrip('.')
            # Обход отсутствия поддомена для главного сайта
            domain_slug = root_domain_slug if domain_slug == '' else domain_slug

        # Полный URL без опциональных GET-параметров (query string)
        path = request.get_full_path().split('?')[0]

        request.http_or_https = http_or_https
        request.root_domain = root_domain
        request.url_domain = url_domain
        request.url_path = path

        # Получение информации о текущем сайте из кэша
        domain = cache_factory('domain', domain_slug)

        # Если сайт НЕ существует - ошибка 500
        if domain is None:
            request.domain_is_published = False
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, такого сайта у нас пока нет. 🙁'),
            ]
            render_messages(request, msgs)
            return render(request, 'error.html', status=500)
        # Если сайт добавлен в БД
        request.domain_id = domain['domain_id']
        request.domain_title = domain['domain_title']
        request.domain_slug = domain['domain_slug']
        request.domain_is_published = domain['domain_is_published']
        request.domain_settings = domain['domain_settings']

        request.city_title = domain['city_title']
        request.city_slug = domain['city_slug']
        request.city_timezone = domain['city_timezone']
        request.city_state = domain['city_state']

        # URL сайта (прокотол + домен) без слэша в конце (для подстановки к относительным ссылкам)
        request.url_protocol_domain = domain['url_protocol_domain']
        # Полный абсолютный URL текущей страницы
        request.url_full = build_absolute_url(request.domain_slug, path)

        # Если город отключен - такой город не существует (ошибка 500)
        if request.city_state is False:
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, этот город не доступен для посещения. 🙁'),
            ]
            render_messages(request, msgs)
            return render(request, 'error.html', status=500)
        # Если город в процессе подготовки - "скоро открытие" (ошибка 503)
        elif request.city_state is None:
            # Сообщение об ошибке
            msgs = [
                message('error', 'Этот город пока в процессе подготовки, скоро открытие.'),
            ]
            render_messages(request, msgs)
            return render(request, 'error.html', status=503)
        # Если город включен
        elif request.city_state is True:
            # Если домен не опубликован - сайт недоступен (ошибка 503)
            if not request.domain_is_published:
                # Сообщение об ошибке
                msgs = [
                    message('error', 'К сожалению, сайт временно недоступен.'),
                    message('error', 'Проводятся технические работы. 🚧'),
                ]
                render_messages(request, msgs)
                return render(request, 'error.html', status=503)
            # Если и город, и домен опубликованы
            else:
                # Активация текущего часового пояса
                if request.city_timezone:
                    # На сайте (но не в админке!) активируется часовой пояс города текущего сайта из БД
                    if settings.BEZANTRAKTA_ADMIN_URL not in request.url_path:
                        current_timezone = request.city_timezone
                    else:
                        current_timezone = request.COOKIES.get('bezantrakta_admin_timezone', 'Europe/Moscow')
                    timezone.activate(current_timezone)
                # Иначе - часовой пояс по умолчанию из базовых настроек проекта (UTC)
                else:
                    timezone.deactivate()

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
                # Сообщение об ошибке
                msgs = [
                    message('error', 'К сожалению, ни один город пока не доступен для показа. 🙁'),
                ]
                render_messages(request, msgs)
                return render(request, 'error.html', status=500)
            else:
                request.cities = list(cities)
                # Псевдоним города из куки `bezantrakta_city`
                request.bezantrakta_city = request.COOKIES.get('bezantrakta_city', None)
