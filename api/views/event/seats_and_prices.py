import uuid

from project.cache import cache_factory
from project.shortcuts import timezone_now

from api.shortcuts import JsonResponseUTF8


def seats_and_prices(request):
    """Получение списка мест и цен на билетов в событии из сервиса продажи билетов."""
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
        heartbeat_timeout_ceiling = heartbeat_timeout + 10
        ts = ticket_service['instance']

        # Параметры для отправки запроса к сервису продажи билетов
        params = {
            'event_id':  event['ticket_service_event'],
        }

        # Попытка получить текущее состояние цен и мест в событии
        sp = cache_factory('seats_and_prices', event_uuid)

        if not sp:
            # Запрос цен и мест в сервисе продажи билетов
            new = ts.seats_and_prices(**params)
            new['updated'] = timezone_now()
            new['in_progress'] = False
            sp = cache_factory('seats_and_prices', event_uuid, obj=new, reset=True)
        else:
            now = timezone_now()
            heartbeat_delta = (now - sp['updated']).total_seconds()
            # print('heartbeat_delta: ', heartbeat_delta)

            if not sp['in_progress'] and heartbeat_delta > heartbeat_timeout:
                # print('NEW REQUEST to ticket service...')
                # Включаем параметр "в процессе обновления", чтобы избежать "гонки" с новыми повторяющимися запросами
                sp['in_progress'] = True
                sp = cache_factory('seats_and_prices', event_uuid, obj=sp, reset=True)

                # Очередной запрос состояния цен и мест
                new = ts.seats_and_prices(**params)
                # Если очередной запрос успешен - выключаем параметр "в процессе обновления" и инвалидируем кэш
                if new['success']:
                    new['updated'] = timezone_now()
                    new['in_progress'] = False
                    sp = cache_factory('seats_and_prices', event_uuid, obj=new, reset=True)
                # Если получаем ошибку - удаляем кэш для гарантированной инвалидации при следующем запросе
                else:
                    cache_factory('seats_and_prices', event_uuid, delete=True)

            # Если кэш зависает в состоянии "в процессе обновления" и не обновляется - он принудительно удаляется
            if sp['in_progress'] and heartbeat_delta > heartbeat_timeout_ceiling:
                cache_factory('seats_and_prices', event_uuid, delete=True)

        # if sp:
        #     print('SEATS & PRICES ', 'updated: ', sp.get('updated'), ' in_progress: ', sp.get('in_progress'))
        #     print('\nprices: # ', len(sp['prices']), str(sp['prices'])[:100])
        #     print('seats: # ', len(sp['seats']), str(sp['seats'])[:100])

        return JsonResponseUTF8(sp)
