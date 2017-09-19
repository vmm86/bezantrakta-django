import datetime
import uuid


def json_serializer(obj):
    """Сериализация JSON с учётом специфических типов данных (``datetime``, ``UUID``).

    Args:
        obj (_): Объект на входе.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        obj = obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        obj = str(obj)
    else:
        obj = None

    return obj
