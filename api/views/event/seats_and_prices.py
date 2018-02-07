from django.http import JsonResponse

from project.cache import cache_factory
# from project.shortcuts import timezone_now


def seats_and_prices(request):
    """Получение списка мест на запрошенное событие из соответствующего сервиса продажи билетов."""
    if request.is_ajax() and request.method == 'GET':
        # UUID события
        event_uuid = request.GET.get('event_uuid', None)
        # Если UUID события не получен - возвращается пустой ответ
        if event_uuid is None:
            return {'seats': [], 'prices': [], }

        # Информация о событии из кэша
        event = cache_factory('event', event_uuid)

        # Информация о сервисе продажи билетов из кэша
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        ts = ticket_service['instance']

        # Параметры для отправки запроса к сервису продажи билетов
        params = {
            'event_id':  event['ticket_service_event'],
            'scheme_id': event['ticket_service_scheme'],
        }

        seats_and_prices = ts.seats_and_prices(**params)

        # # Попытка получить текущее состояние мест и цен в событии
        # seats_and_prices = cache_factory('seats_and_prices', event_uuid)

        # if not seats_and_prices:
        #     # Запрос мест и цен в сервисе продажи билетов
        #     new = ts.seats_and_prices(**params)
        #     new['updated'] = timezone_now()
        #     seats_and_prices = cache_factory('seats_and_prices', event_uuid, obj=new, reset=True)
        # else:
        #     now = timezone_now()
        #     heartbeat_delta = (now - seats_and_prices['updated']).seconds
        #     print('now: ', now)
        #     print('updated: ', seats_and_prices['updated'])
        #     print('heartbeat_delta: ', heartbeat_delta)
        #     print('ts[heartbeat_timeout]', ticket_service['settings']['heartbeat_timeout'])

        #     if heartbeat_delta > ticket_service['settings']['heartbeat_timeout']:
        #         new = ts.seats_and_prices(**params)
        #         new['updated'] = timezone_now()
        #         seats_and_prices = cache_factory('seats_and_prices', event_uuid, obj=new, reset=True)

        # print('seats_and_prices: #', len(seats_and_prices['seats']), str(seats_and_prices)[:100], '...')

        # # print('seats_and_prices: ', seats_and_prices)

        return JsonResponse(seats_and_prices, safe=False)
