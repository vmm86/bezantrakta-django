from django.http.request import split_domain_port
from django.utils.deprecation import MiddlewareMixin


class CurrentDomainMiddleware(MiddlewareMixin):
    """
    Middleware sets `domain` attributes to request object.
    """
    def process_request(self, request):
        if request:
            host = request.get_host()
            domain, port = split_domain_port(host)
            request.domain_slug = domain

            full_path = request.get_full_path()
            # Path without optional query string and boundary slashes
            path = full_path.split('?')[0].strip('/')
            request.domain_path = path

            # try:
            #     # First attempt to look up the domain with/without port.
            #     if host not in DOMAIN_CACHE:
            #         DOMAIN_CACHE[host] = self.get(domain__iexact=host)
            #     return DOMAIN_CACHE[host]
            # except Domain.DoesNotExist:
            #     # Fallback to looking up domain after stripping port.
            #     domain, port = split_domain_port(host)
            #     if domain not in DOMAIN_CACHE:
            #         DOMAIN_CACHE[domain] = self.get(domain__iexact=domain)
            #     return DOMAIN_CACHE[domain]
