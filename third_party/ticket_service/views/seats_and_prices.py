from django.http import JsonResponse

from project.cache import cache_factory


def seats_and_prices(request):
    """
    Получение списка мест на запрошенное событие из соответствующего сервиса продажи билетов.
    """
    if request.is_ajax() and request.method == 'GET':
        # Идентификатор сервиса продажи билетов
        ticket_service_id = request.GET.get('ticket_service_id', None)

        # Параметры для отправки запроса к сервису продажи билетов
        params = {}
        keys = (
            ('event_id', int,),
            ('scheme_id', int,),
        )
        for k in keys:
            params[k[0]] = k[1](request.GET.get(k[0], 0))

        # print('event_id:', params['event_id'], type(params['event_id']))
        # print('scheme_id:', params['scheme_id'], type(params['scheme_id']))

        if ticket_service_id is not None:
            ticket_service = cache_factory('ticket_service', ticket_service_id)
            ts = ticket_service['instance']

            seats_and_prices = ts.seats_and_prices(**params)
        else:
            seats_and_prices = {}
            seats_and_prices['seats'] = []
            seats_and_prices['prices'] = []

        return JsonResponse(seats_and_prices, safe=False)
