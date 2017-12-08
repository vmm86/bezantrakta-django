import datetime


def json_serializer(obj):
    """Сериализация объекта в JSON с учётом специфических типов данных.

    Args:
        obj (str|None): Объект на входе.
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        obj = obj.isoformat()
    else:
        obj = str(obj)

    return obj
