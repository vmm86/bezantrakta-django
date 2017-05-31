from django.http.request import split_domain_port
from django.utils.deprecation import MiddlewareMixin

from bezantrakta.domain.models import Domain


class CurrentDomainMiddleware(MiddlewareMixin):
    """
    Middleware sets `domain` attributes to request object.
    """
    def process_request(self, request):
        host = request.get_host()
        url_domain, url_port = split_domain_port(host)
        domain = Domain.objects.select_related('city').values('id', 'city__title', 'city__slug').get(slug=url_domain)

        request.domain_slug = url_domain
        request.domain_id = domain['id']

        full_path = request.get_full_path()
        # Path without optional query string
        path = full_path.split('?')[0]
        # Path without boundary slashes
        request.url_path = path.strip('/')
        request.url_full = ''.join((url_domain, path,))

        request.city_title = domain['city__title']
        request.city_slug = domain['city__slug']
