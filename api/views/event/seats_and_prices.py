import uuid

from project.cache import cache_factory
from project.shortcuts import timezone_now

from api.shortcuts import JsonResponseUTF8


def seats_and_prices(request):
    """Получение списка мест на запрошенное событие из соответствующего сервиса продажи билетов."""
    if request.is_ajax() and request.method == 'GET':
        # UUID события
        event_uuid = request.GET.get('event_uuid', None)
        # Если UUID события не получен - возвращается пустой ответ
        if event_uuid is None:
            response = {'success': False, 'message': 'Отсутствует UUID события'}
            return JsonResponseUTF8(response)
        try:
            event_uuid = uuid.UUID(event_uuid)
        except (TypeError, ValueError):
            response = {'success': False, 'message': 'Получен неправильный UUID события'}
            return JsonResponseUTF8(response)

        # Информация о событии из кэша
        event = cache_factory('event', event_uuid)

        # Информация о сервисе продажи билетов из кэша
        ticket_service = cache_factory('ticket_service', event['ticket_service_id'])
        heartbeat_timeout = ticket_service['settings']['heartbeat_timeout']
        ts = ticket_service['instance']

        # Параметры для отправки запроса к сервису продажи билетов
        params = {
            'event_id':  event['ticket_service_event'],
        }

        # seats_and_prices = ts.seats_and_prices(**params)

        # Попытка получить текущее состояние мест и цен в событии
        seats_and_prices = cache_factory('seats_and_prices', event_uuid)

        if not seats_and_prices:
            # Запрос мест и цен в сервисе продажи билетов
            new = ts.seats_and_prices(**params)
            now = timezone_now()
            new['updated'] = now
            new['in_progress'] = False
            seats_and_prices = cache_factory('seats_and_prices', event_uuid, obj=new, reset=True)
        else:
            now = timezone_now()
            heartbeat_delta = (now - seats_and_prices['updated']).total_seconds()
            print('\nnow: {:%Y-%m-%d %H:%M:%S}'.format(now))
            print('heartbeat_delta: ', heartbeat_delta)

            if heartbeat_delta > heartbeat_timeout and not seats_and_prices['in_progress']:
                print('NEW REQUEST to ticket service...')
                # Включаем параметр "в процессе обновления", чтобы избежать "гонки"" с новыми повторяющимися запросами
                seats_and_prices['in_progress'] = True
                seats_and_prices = cache_factory('seats_and_prices', event_uuid, obj=seats_and_prices, reset=True)

                # Очередной запрос состояния мест и цен
                new = ts.seats_and_prices(**params)
                # Если очередной запрос успешен - выключаем параметр "в процессе обновления" и инвалидируем кэш
                if new['success']:
                    new['updated'] = timezone_now()
                    new['in_progress'] = False
                    seats_and_prices = cache_factory('seats_and_prices', event_uuid, obj=new, reset=True)
                # Если получаем ошибку - удаляем кэш для гарантированной инвалидации при следующем запросе
                else:
                    cache_factory('seats_and_prices', event_uuid, delete=True)

        print('SEATS AND PRICES ', 'updated: ', seats_and_prices['updated'], ' in_progress: ', seats_and_prices['in_progress'])
        # print('\nprices: # ', len(seats_and_prices['prices']), str(seats_and_prices['prices'])[:100])
        print('\nseats: # ', len(seats_and_prices['seats']), str(seats_and_prices['seats'])[:100])

        # print('seats_and_prices: ', seats_and_prices)

        return JsonResponseUTF8(seats_and_prices)
