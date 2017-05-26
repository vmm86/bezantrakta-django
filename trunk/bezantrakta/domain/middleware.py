from django.http.request import split_domain_port
from django.utils.deprecation import MiddlewareMixin

from bezantrakta.domain.models import Domain


class CurrentDomainMiddleware(MiddlewareMixin):
    """
    Middleware sets `domain` attributes to request object.
    """
    def process_request(self, request):
        host = request.get_host()
        domain, port = split_domain_port(host)
        request.domain = domain

        full_path = request.get_full_path()
        # Path without optional query string and boundary slashes
        path = full_path.split('?')[0].strip('/')
        request.url_path = path

        city = Domain.objects.only('city__title').get(slug=domain)
        request.city_title = city
