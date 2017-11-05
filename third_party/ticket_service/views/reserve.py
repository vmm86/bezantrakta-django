from django.http import JsonResponse

from third_party.ticket_service.cache import ticket_service_instance


def reserve(request):
    """Добавление или удаление места в предварительном резерве мест (корзина заказа)."""
    if request.is_ajax() and request.method == 'POST':
        # Параметры для получения экземпляра класса сервиса продажи билетов
        ticket_service_id = request.POST.get('ticket_service_id')

        # Параметры для создания предварительного резерва указанного места
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
        for k in keys:
            params[k[0]] = request.POST.get(k[0])
            # Преобразование типов (если необходимо)
            # if k[1] is int:
            #     params[k[0]] = None if params[k[0]] == '' else params[k[0]]
            #     if params[k[0]] is not None:
            #         params[k[0]] = int(params[k[0]])
            #     else:
            #         pass

        # Экземпляр класса сервиса продажи билетов
        ts = ticket_service_instance(ticket_service_id)

        # Универсальный метод для работы с предварительным резервом мест
        reserve = ts.reserve(**params)

        # Формирование ответа
        response = {}

        for k in keys:
            response[k[0]] = params[k[0]]

        response['success'] = True if reserve['success'] else False

        if not reserve['success']:
            response['code'] = reserve['code']
            response['message'] = reserve['message']

        return JsonResponse(response, safe=False)
