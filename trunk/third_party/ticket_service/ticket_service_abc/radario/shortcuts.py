import dateutil.parser
from datetime import datetime
from decimal import Decimal


def humanize_with_type_casting(iterable, output_mapping):
    """
    Конвертация ключей в человекопонятные значения.

    Args:
        iterable (dict): Ответ метода.
        output_mapping (dict): Словарь для замены.
    """
    for external, internal in output_mapping.items():
        if internal is None:
            try:
                iterable.pop(external)
            except KeyError:
                pass
        else:
            try:
                iterable[internal[0]] = iterable.pop(external)
            except KeyError:
                pass
            else:
                # Если получено пустое значение  - попытка задать значения по умолчанию
                if iterable[internal[0]] is None:
                    try:
                        internal[2] is not None
                    except (IndexError, KeyError):
                        pass
                    else:
                        iterable[internal[0]] = internal[2]
                # Если получено НЕпустое значение - приведение типы данных
                else:
                    if internal[1] is datetime:
                        # '2017-09-29T16:00:00.000+00:00'
                        iterable[internal[0]] = dateutil.parser.parse(iterable[internal[0]])
                    elif internal[1] is Decimal:
                        iterable[internal[0]] = Decimal(iterable[internal[0]]).quantize(Decimal('1.00'))
                    else:
                        pass


def prettify_json_response(response, output_mapping):
    """
    Конвертация XML-ответа в структуру данных Python и последующая обработка.

    Args:
        response (dict): Ответ конкретного метода API.
        output_mapping (dict): Словарь для замены.

    Returns:
        list, dict: Обработанный ответ конкретного метода API.
    """
    response_code = 0 if response['success'] else response['error']['errorCode']
    response_message = 'OK' if response['success'] else response['error']['message']

    # Если ответ успешен
    if response_code == 0:
        # Тело ответа с необходимыми данными, либо сообщение об успешном или НЕуспешном ответе
        try:
            iterable = response['data']['items']
        except KeyError:
            try:
                iterable = response['data']
            except KeyError:
                if response['success']:
                    return {'code': 0, 'message': 'OK', }
                else:
                    return {'code': response_code, 'message': response_message, }

        # Если в ответе - множество записей
        if type(iterable) is list:
            # Конвертация ключей в человекопонятные значения
            for d in iterable:
                humanize_with_type_casting(d, output_mapping)
        # Если в ответе - одна запись
        elif type(iterable) is dict:
            # Конвертация ключей в человекопонятные значения
            humanize_with_type_casting(iterable, output_mapping)
        return iterable
    # Если ответ НЕуспешен
    else:
        return {'code': response_code, 'message': response_message, }
