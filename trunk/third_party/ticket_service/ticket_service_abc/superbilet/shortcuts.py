import xmltodict

from decimal import Decimal


RESPONSE_CODES = {
    # Общие коды ответа
    0:  'Успешный результат',
    1:  'Место занято/отсутствует или событие неактивно (прошло, отменено, продажа не разрешена)',
    2:  'Ошибка интерфейса - неверный формат данных',
    3:  'Ошибка доступа к базе данных',
    4:  'Неверный номер сессии или снята предварительная бронь',
    5:  'Ошибка авторизации',
    6:  'Системная ошибка в работе шлюза',
    7:  'Отсутствует шлюз для подключения (версия V2) или отсутствует покупатель',
    # Только в "Супербилет-Театр"
    8:  'Не заполнены Ф.И.О. покупателя',
    9:  'Не заполнены контактные данные покупателя (телефон или email)',
    10: 'Не указана транзакция в методе SetSoldExt',
    11: 'Не указана дата транзакции в методе SetSoldExt',
    12: 'Не указано время транзакции в методе SetSoldExt',
    13: 'Заказ оплачен - место не подлежит удалению',
    # Только в "Супербилет-Театр" версии 6.2.P+
    14: 'Пользователь не является пользователем шлюза',
    15: 'Пользователю запрещен доступ к шлюзу',
}

# Значения параметра `actiondone` в методе `GetLog`
LOG_OPERATIONS = {
    'PlacePreRes':
        'Не найдено место для предварительного бронирования.',
    'ErrorPreRes':
        'При предварительном бронировании произошла ошибка (откат транзакции).',
    'FailPreRes':
        'При предварительном бронировании место не было забронировано.',
    'PreRes':
        'Предварительное бронирование успешно создано.',
    'NoSessionFreePreRes':
        'При удалении предварительного бронирования не найден номер сессии.',
    'NoPlaceFreePreRes':
        'При удалении предварительного бронирования не найдено место.',
    'FailFreePreRes':
        'При удалении предварительного бронирования произошла ошибка.',
    'FreePreRes':
        'Предварительное бронирование успешно удалено.',
    'NoSessionSetRes':
        'При бронировании не найден номер сессии.',
    'NoPlaceSetRes':
        'При бронировании не найдено место.',
    'FailSetRes':
        'При бронировании произошла ошибка (не найдено предварительное бронирование или сессия).',
    'ErrorSetRes':
        'При бронировании произошла ошибка.',
    'SetRes':
        'Бронирование успешно создано.',
    'NoSessionFreeRes':
        'При удалении бронирования не найден номер сессии.',
    'NoPlaceFreeRes':
        'При удалении бронирования не найдено место.',
    'FailFreeRes':
        'При удалении бронирования произошла ошибка (не найдено предварительное бронирование или сессия).',
    'ErrorFreeRes':
        'При удалении бронирования произошла ошибка.',
    'NoReservationFreeRes':
        'Нет бронирования для места.',
    'FreeRes':
        'Бронирование успешно удалено.',
    'NoSessionSetSold':
        'При продаже не найден номер сессии.',
    'NoReservationSetSold':
        'При продаже не найдено бронирование.',
    'NoPlaceSetSold':
        'При продаже не найдено место.',
    'ErrorSetSold':
        'При продаже произошда ошибка.',
    'FailSetSold':
        'При продаже произошда ошибка (не найдено бронирование или сессия).',
    'SetSold':
        'Продажа успешно создана.',
}


def humanize_with_type_casting(iterable, output_mapping):
    """
    Конвертация ключей в человекопонятные значения.
    Приведение типов в содержимом словаря (по умолчанию - str).
    """
    for external, internal in output_mapping.items():
        if internal is None:
            try:
                iterable.pop('@' + external)
            except KeyError:
                pass
        else:
            try:
                iterable[internal[0]] = iterable.pop('@' + external)
            except KeyError:
                pass
            else:
                if iterable[internal[0]] != '':
                    if internal[1] is int:
                        iterable[internal[0]] = int(iterable[internal[0]])
                    elif internal[1] is Decimal:
                        iterable[internal[0]] = Decimal(iterable[internal[0]]).quantize(Decimal('1.00'))
                    elif internal[1] is bool:
                        true_values = ['True', 'true', 1, '1', 'y', 'yes', ]
                        iterable[internal[0]] = True if iterable[internal[0]] in true_values else False
                    else:
                        pass


def prettify_xml_response(response, output_mapping):
    """
    Конвертация XML-ответа в структуру данных Python и последующая обработка.
    """
    response = xmltodict.parse(response, dict_constructor=dict, attr_prefix='@', cdata_key='#text')
    # print(response)
    response_code = int(response['GateAnswer']['AnswerResult']['ResultCode'])
    response_count = int(response['GateAnswer']['AnswerResult']['RecordCount'])
    try:
        response_message = response['GateAnswer']['AnswerResult']['ResultText']
    except KeyError:
        response_message = ''

    # Если ответ успешен
    if response_code == 0:
        # Тело ответа с необходимыми данными, если они есть
        if response_count > 0:
            iterable = response['GateAnswer']['AnswerBody']['Row']
            # print(iterable)

            # Если в ответе - множество записей
            if type(iterable) is list:
                # Ключи в нижнем регистре
                iterable = [{k.lower(): v for k, v in d.items()} for d in iterable]
                # Конвертация ключей в человекопонятные значения и приведение типов (по умолчанию - str)
                for d in iterable:
                    humanize_with_type_casting(d, output_mapping)
            # Если в ответе - одна запись
            elif type(iterable) is dict:
                # Ключи в нижнем регистре
                iterable = {k.lower(): v for k, v in iterable.items()}
                # Конвертация ключей в человекопонятные значения и приведение типов (по умолчанию - str)
                humanize_with_type_casting(iterable, output_mapping)
                # Если ответ пришёл с ошибкой
                if iterable['result_code'] != 0:
                    code = iterable['result_code']
                    message = RESPONSE_CODES[code]
                    return {'code': code, 'message': message, }
            return iterable
        else:
            return {'code': response_code, 'message': 'К сожалению, по вашему запросу ничего не найдено.', }
    # Если ответ НЕуспешен
    else:
        return {'code': response_code, 'message': response_message, }
