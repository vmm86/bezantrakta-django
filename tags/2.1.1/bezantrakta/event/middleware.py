import datetime

from django.http.request import split_domain_port
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, Resolver404


class EventCalendarMiddleware(MiddlewareMixin):
    """Получение даты, выбранной в календаре её добавление в request."""
    def process_request(self, request):
        host = request.get_host()
        url_domain, url_port = split_domain_port(host)
        url_path = request.get_full_path().split('?')[0]
        # url_full = '{domain}{path}'.format(domain=url_domain, path=path)

        try:
            resolved_view = resolve(url_path)

            if resolved_view.view_name == 'event:calendar':
                current_timezone = request.city_timezone
                calendar_date = current_timezone.localize(
                    datetime.datetime(
                        year=int(resolved_view.kwargs['year']),
                        month=int(resolved_view.kwargs['month']),
                        day=int(resolved_view.kwargs['day']),
                    )
                )
            else:
                calendar_date = timezone.now().date
        except Resolver404:
            calendar_date = timezone.now().date

        request.calendar_date = calendar_date
