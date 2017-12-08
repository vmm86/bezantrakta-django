import datetime
import uuid


def json_serializer(obj):
    """Сериализация объекта в JSON с учётом специфических типов данных (``datetime.datetime``, ``uuid.UUID``).

    Args:
        obj (str|None): Объект на входе.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        obj = obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        obj = str(obj)
    else:
        obj = None

    return obj
