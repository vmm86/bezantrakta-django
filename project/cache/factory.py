from bezantrakta.event.cache import EventCache
from third_party.ticket_service.cache import TicketServiceCache, TicketServiceSchemeSectorCache
from third_party.payment_service.cache import PaymentServiceCache


CACHE_CLASSES = (EventCache, TicketServiceCache, TicketServiceSchemeSectorCache, PaymentServiceCache, )


def cache_factory(entity, object_id, reset=False, **kwargs):
    """Фабрика для инстанцирования класса для кэширования.

    Args:
        entity (str): Название модели или другой сущности для создания кэша.
        object_id (int|str|uuid.UUID): Идентификатор записи в БД.
        reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.
        **kwargs: Дополнительные параметры, коотрые могут понадобится при обработке получаемого кэша.

    Returns:
        dict: Запрошенный кэш.
    """
    for cls in CACHE_CLASSES:
        if entity in cls.entities:
            cache = cls(entity, object_id, reset, **kwargs)
            return cache.value
