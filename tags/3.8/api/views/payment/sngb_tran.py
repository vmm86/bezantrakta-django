import logging
import simplejson as json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from project.shortcuts import timezone_now


@csrf_exempt
def sngb_tran(request):
    """Обработка возвратов в СургутНефтеГазБанке."""
    now = timezone_now()
    logger = logging.getLogger('bezantrakta.refund')
    logger.info('\n----Обработка возврата СНГБ----')
    logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(now))

    # {
    # 'result': ['CAPTURED'],
    # 'responsecode': ['00'],
    # 'udf1': ['185'],
    # 'udf2': ['def744ae-1cd3-4ca9-a0e9-1c17fd83d4be'],
    # 'udf3': ['Ïîñòîðîííèì Â'],
    # 'udf4': ['678c81c2-920f-4758-8ab7-3d7d136c1f4c'],
    # 'udf5': ['5735609e6c523fe0e6e6c64592a82c5481ac2fd1'],
    # 'trackid': ['16428'],
    # 'paymentid': ['9321996201181130']
    # 'tranid': ['2991167271181130'],
    # 'ref': ['217122011273'],
    # 'eci': ['7'],
    # }

    response_params = {
        'result':       'payment_status',
        'responsecode': 'payment_code',
        'udf1':         'event_id',
        'udf2':         'event_uuid',
        'udf3':         'customer_name',
        'udf4':         'order_uuid',
        'trackid':      'order_id',
        'paymentid':    'payment_id',
        'tranid':       'transaction_id',

        'ref': 'ref',
        'eci': 'eci',

        'error':        'code',
        'errortext':    'message',
    }

    data = {}

    if request.method == 'POST' and request.POST:
        logger.info('POST: {}'.format(request.POST))
        # Получение данных из POST-запроса
        for external, internal in response_params.items():
            data[internal] = request.POST.get(external, None)
    elif request.method == 'GET' and request.GET:
        logger.info('GET: {}'.format(request.GET))
        # Получение данных из GET-запроса
        for external, internal in response_params.items():
            data[internal] = request.GET.get(external, None)

    logger.info('data: '.format(data))

    response = {}

    if data:
        # Приведение кода оплаты к int, если строка является числом
        # (у успешной оплаты статус равен '00')
        try:
            data['payment_code'] = int(data['payment_code'])
        except ValueError:
            pass

        # Преобразование ФИО покупателя из кракозябр на входе (CP1252 > CP1251)
        data['customer_name'] = data['customer_name'].encode('cp1252').decode('cp1251')

        # Логирование полученных данных
        for param in response_params.values():
            if data[param] is not None:
                logger.info('{param}: {value}'.format(
                    param=param,
                    value=data[param])
                )

        # Успешный запрос на оплату
        if data['payment_code'] == 0:
            response['success'] = True

            logger.info('\nВозврат в СНГБ завершился успешно\n')

        # НЕуспешный запрос на оплату
        else:
            response['success'] = False

            logger.info('\nВозврат в СНГБ завершился НЕуспешно\n')

            if data['code']:
                response['code'] = data['code']
                response['message'] = data['message']

    else:
        response['success'] = False

    return HttpResponse(json.dumps(response))
