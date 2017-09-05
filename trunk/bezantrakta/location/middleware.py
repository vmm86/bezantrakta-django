import simplejson as json

from django.conf import settings
from django.db.models import CharField, Case, When, Value, Q
from django.http.request import split_domain_port
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from project.shortcuts import message, render_messages

from .models import City, Domain


class CurrentLocationMiddleware(MiddlewareMixin):
    """
    Получение информации о текущем городе и домене и её добавление в request.
    """
    def process_request(self, request):
        host = request.get_host()
        url_domain, url_port = split_domain_port(host)
        root_domain = settings.BEZANTRAKTA_ROOT_DOMAIN
        root_domain_slug = settings.BEZANTRAKTA_ROOT_DOMAIN_SLUG
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
                'title',
                'slug',
                'is_published',
                'settings',
                'city_id',
                'city__title',
                'city__slug',
                'city__timezone',
                'city__state',
            ).get(slug=domain_slug)
        # Если домен НЕ добавлен в БД - такой сайт не существует (ошибка 500)
        except Domain.DoesNotExist:
            # Сообщение об ошибке
            msgs = [
                message('error', 'К сожалению, такого сайта у нас пока нет. 😞'),
            ]
            render_messages(request, msgs)
            return redirect('error_500')
        # Если домен добавлен в БД
        else:
            request.domain_id = domain['id']
            request.domain_title = domain['title']
            request.domain_slug = domain['slug']
            request.domain_is_published = domain['is_published']
            request.domain_settings = json.loads(domain['settings'])

            request.city_title = domain['city__title']
            request.city_slug = domain['city__slug']
            request.city_timezone = domain['city__timezone']
            request.city_state = domain['city__state']

            # Если город отключен - такой город не существует (ошибка 500)
            if request.city_state is False:
                # Сообщение об ошибке
                msgs = [
                    message('error', 'К сожалению, этот город не доступен для посещения. 😞'),
                ]
                render_messages(request, msgs)
                return redirect('error_500')

            # Если город в процессе подготовки - "скоро открытие" (ошибка 503)
            elif request.city_state is None:
                # Сообщение об ошибке
                msgs = [
                    message('error', 'Этот город пока в процессе подготовки, скоро открытие.'),
                ]
                render_messages(request, msgs)
                return redirect('error_503')

            # Если город включен
            elif request.city_state is True:
                # Если домен не опубликован - сайт недоступен (ошибка 503)
                if not request.domain_is_published:
                    # Сообщение об ошибке
                    msgs = [
                        message('error', 'К сожалению, сайт временно недоступен.'),
                        message('error', 'Проводятся технические работы.'),
                    ]
                    render_messages(request, msgs)
                    return redirect('error_503')
                # Если и город, и домен опубликованы
                else:
                    # Полный URL без опциональных GET-параметров (query string)
                    path = request.get_full_path().split('?')[0]

                    request.root_domain = settings.BEZANTRAKTA_ROOT_DOMAIN
                    request.url_domain = url_domain
                    request.url_path = path
                    request.url_full = '{domain}{path}'.format(domain=url_domain, path=path)

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
                        message('error', 'К сожалению, ни один город пока не доступен для показа. 😞'),
                    ]
                    render_messages(request, msgs)
                    return redirect('error_500')
                else:
                    request.cities = list(cities)
                    # Псевдоним города из куки `bezantrakta_city`
                    request.bezantrakta_city = request.COOKIES.get('bezantrakta_city', None)
