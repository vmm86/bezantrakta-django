from django.http import JsonResponse

from project.cache import cache_factory


def reserve(request):
    """Добавление или удаление места в предварительном резерве мест (корзина заказа)."""
    if request.is_ajax() and request.method == 'POST':
        # Идентификатор сервиса продажи билетов
        ticket_service_id = request.POST.get('ticket_service_id', None)

        # Параметры для отправки запроса к сервису продажи билетов
        params = {}
        keys = (
            ('action', str,),
            ('order_uuid', str,),
            ('event_id', int,),
            ('sector_id', int,),
            ('sector_title', str,),
            ('row_id', int,),
            ('seat_id', int,),
            ('seat_title', str,),
            ('price_group_id', int,),
            ('price', str,),
            ('price_order', int,),
        )
        # Преобразование типов
        for k in keys:
            try:
                params[k[0]] = k[1](request.POST.get(k[0], None))
            except ValueError:
                params[k[0]] = None

        # Формирование ответа
        response = {}

        for k in keys:
            response[k[0]] = params[k[0]]

        if ticket_service_id is not None:
            # Экземпляр класса сервиса продажи билетов
            ticket_service = cache_factory('ticket_service', ticket_service_id)
            ts = ticket_service['instance']

            # Универсальный метод для работы с предварительным резервом мест
            reserve = ts.reserve(**params)
            # print('reserve: ', reserve)

            response['success'] = True if reserve['success'] else False

            if not reserve['success']:
                response['code'] = reserve['code']
                response['message'] = reserve['message']
        else:
            response['false'] = True

        return JsonResponse(response, safe=False)
