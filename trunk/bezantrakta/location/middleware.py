from django.conf import settings
from django.http.request import split_domain_port
from django.http.response import HttpResponse
from django.template import loader
from django.utils.deprecation import MiddlewareMixin

from bezantrakta.location.models import Domain


class CurrentDomainMiddleware(MiddlewareMixin):
    """
    Получение информации о текущем домене и её добавление в request.
    """
    def render_error_page(self, context, request, status_code=404):
        template = loader.get_template('empty.html')
        return HttpResponse(template.render(context, request), status=status_code)

    def process_request(self, request):
        host = request.get_host()
        url_domain, url_port = split_domain_port(host)
        # Если URL содержит основной домен, указанный в настройках, вытаскиваем его поддомен(ы)
        if url_domain.endswith(settings.ROOT_DOMAIN):
            domain_slug = url_domain[:-len(settings.ROOT_DOMAIN)].rstrip('.')
            # Обход отсутствия поддомена для воронежского сайта
            domain_slug = 'vrn' if domain_slug == '' else domain_slug

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
        # Если домена НЕ добавлен в БД - такой сайт не существует (ошибка 500)
        except Domain.DoesNotExist:
            context = {
                'title': """Запрошенный сайт не существует""",
                'message': """Извините, запрошенный Вами сайт не существует.""",
            }
            return self.render_error_page(context, request, 500)
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
                    'message': """Сайты в этом городе ещё не открыты для посещения.
                    Попробуйте зайти позднее.""",
                }
                return self.render_error_page(context, request, 503)
            # Если домен не опубликован - ошибка 503
            elif not request.domain_is_published:
                context = {
                    'title': """Сайт на данный момент надоступен""",
                    'message': """Извините, сейчас проводятся технические работы, сайт временно недоступен.
                    Попробуйте зайти позднее.""",
                }
                return self.render_error_page(context, request, 503)
            # Если и город, и домен опубликованы
            else:
                full_path = request.get_full_path()
                # Path without optional query string
                path = full_path.split('?')[0]
                # Path without boundary slashes
                request.url_path = path.strip('/')
                request.url_full = ''.join((url_domain, path,))
