import simplejson as json
from functools import wraps


def dumps_json_from_object(obj):
    return json.dumps(obj, ensure_ascii=False) if obj else '{}'


def default_json_settings(obj):
    """Получение JSON-настроек по умолчанию при создании новой записи в модели.

    Декорирует callable-функцию, которая указывается в параметре ``default`` для требуемого поля модели.

    Args:
        obj (dict|collections.OrderedDict): Объект, содержащий настройки по умолчанию.

    Returns:
        function: Настройки по умолчанию в виде строки для записи в БД.
    """
    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            return dumps_json_from_object(obj)
        return wrapper
    return decorator
