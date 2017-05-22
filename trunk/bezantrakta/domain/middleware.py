from django.http.request import split_domain_port
from django.utils.deprecation import MiddlewareMixin


class CurrentDomainMiddleware(MiddlewareMixin):
    """
    Middleware that sets `domain` attribute to request object.
    """
    def process_request(self, request):
        if request:
            host = request.get_host()
            domain, port = split_domain_port(host)
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
            request.domain = domain
