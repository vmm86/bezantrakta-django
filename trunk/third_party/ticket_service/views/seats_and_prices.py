from django.http import JsonResponse

from project.cache import cache_factory


def seats_and_prices(request):
    """
    Получение списка мест на запрошенное событие из соответствующего сервиса продажи билетов.
    """
    if request.is_ajax() and request.method == 'GET':
        # Параметры для получения экземпляра класса сервиса продажи билетов
        ticket_service_id = request.GET.get('ticket_service_id')

        # Параметры для получения списка мест в указанном событии/зале
        event_id = request.GET.get('event_id')
        venue_id = request.GET.get('venue_id')

        ticket_service = cache_factory('ticket_service', ticket_service_id)
        ts = ticket_service['instance']

        seats = ts.seats_and_prices(
            event_id=event_id,
            venue_id=venue_id
        )

        return JsonResponse(seats, safe=False)
