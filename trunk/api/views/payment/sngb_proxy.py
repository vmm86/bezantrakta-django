import logging
from urllib.parse import urlencode

from django.http import HttpResponse
from django.urls.base import reverse
from django.views.decorators.csrf import csrf_exempt

from project.shortcuts import build_absolute_url, timezone_now


@csrf_exempt
def sngb_proxy(request):
    """Предобработка успешной или НЕуспешной оплаты в СургутНефтеГазБанке."""
    now = timezone_now()
    logger = logging.getLogger('bezantrakta.order')
    logger.info('\n----Предоработка оплаты в СНГБ----')
    logger.info('{:%Y-%m-%d %H:%M:%S} (UTC)'.format(now))

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

        'error':        'code',
        'errortext':    'message',

        # 'ref':          'ref',           # Уникальный идентификатор операции, созданный авторизационной системой
        # 'cvv2response': 'cvv2response',  # Код, определяющий валидность CVV2
        # 'postdate':     'postdate',      # Дата транзакции
        # 'auth':         'auth',          # Код авторизации
        # 'avr':          'avr',           # Код результата проверки адреса (используется в некоторых странах)
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

    # Приведение кода оплаты к int, если строка является числом
    # (у успешной оплаты статус равен '00')
    try:
        data['payment_code'] = int(data['payment_code'])
    except ValueError:
        pass

    logger.info('data: ', data)

    # Логирование полученных данных
    for param in response_params.values():
        if data[param] is not None:
            logger.info('{param}: {value}'.format(
                param=param,
                value=data[param])
            )

    # Базовый URL для последующего редиректа
    redirect_base = 'REDIRECT='

    redirect_url = ''

    # Успешный запрос на оплату
    if data['payment_code'] == 0:
        data['success'] = True

        logger.info('\nОплата в СНГБ завершилась успешно')

        qs = {
            # 'success':    data['success'],
            # 'payment_id': data['payment_id'],
            'event_uuid': data['event_uuid'],
            'order_uuid': data['order_uuid'],
        }
        urlencoded_qs = urlencode(qs)

        redirect_url = '{redirect_base}{redirect_url}?{urlencoded_qs}'.format(
            redirect_base=redirect_base,
            redirect_url=build_absolute_url(
                request.domain_slug, reverse('api:payment__success')
            ),
            urlencoded_qs=urlencoded_qs,
        )
    # НЕуспешный запрос на оплату
    else:
        data['success'] = False

        logger.info('\nОплата в СНГБ завершилась НЕуспешно')

        qs = {
            # 'success':    data['success'],
            # 'payment_id': data['payment_id'],
            'event_uuid': data['event_uuid'],
            'order_uuid': data['order_uuid'],
        }

        if data['code']:
            qs['code'] = data['code']
            qs['message'] = data['message']

        urlencoded_qs = urlencode(qs)

        redirect_url = '{redirect_base}{redirect_url}?{urlencoded_qs}'.format(
            redirect_base=redirect_base,
            redirect_url=build_absolute_url(
                request.domain_slug, reverse('api:payment__error')
            ),
            urlencoded_qs=urlencoded_qs,
        )

    return HttpResponse(redirect_url)
