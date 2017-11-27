import simplejson as json
from abc import ABC, abstractmethod, abstractproperty

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from project.shortcuts import debug_console, json_serializer


class ProjectCache(ABC):
    """
    Абстрактный класс-родитель конкретных классов кэширования записи какой-либо модели проекта с пред- и постобработкой.

    Attributes:
        entities (tuple): Перечень моделей или других сущностей для создания кэша (указывается в дочерних классах).
        key (str): Текущий ключ для создания/обновления/получения кэша.
        value (dict): Текущее обработанное значение кэша для вывода.
    """
    entities = ()
    key = ''
    value = None

    def __init__(self, entity, object_id, reset=False, **kwargs):
        """Конструктор класса.

        Args:
            object_id (int|str|uuid.UUID): Идентификатор записи в БД.
            reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.
        """
        super().__init__()

        self.key = '{entity}.{object_id}'.format(entity=entity, object_id=object_id)
        self.value = cache.get(self.key)
        debug_console('cache_key:', self.key)
        debug_console('cache_value_postprocessed:', self.value, type(self.value))

        if reset:
            cache.delete(self.key)

        if not self.value or reset:
            try:
                self.value = dict(self.get_model_object(object_id))
            except ObjectDoesNotExist:
                return None
            else:
                self.cache_preprocessing(**kwargs)

                cache.set(self.key, json.dumps(self.value, ensure_ascii=False, default=json_serializer))
        else:
            self.value = json.loads(self.value)
            self.cache_postprocessing(**kwargs)

        debug_console('cache_value_postprocessed:', self.value, type(self.value))

    def __str__(self):
        return '{cls}({key})'.format(
            cls=self.__class__.__name__,
            key=self.key,
        )

    @abstractmethod
    def get_model_object(self, object_id):
        """Получение объекта необходимой модели в БД запросом к ``self.model``.

        Args:
            object_id (int|str|uuid.UUID): Идентификатор записи в БД.

        Returns:
            django.db.models.query.QuerySet: Объект конкретной модели в БД.
        """
        pass

    @abstractmethod
    def cache_preprocessing(self, **kwargs):
        """Предобработка значения кэша перед его сохранением.

        Args:
            **kwargs: Дополнительные параметры, коотрые могут понадобится при обработке получаемого кэша.

        No Longer Returned:
            dict: Обработанное значение для сохранения в кэш.
        """
        pass

    @abstractmethod
    def cache_postprocessing(self, **kwargs):
        """Постобработка ранее полученного значения кэша перед его возвращением.

        Args:
            **kwargs: Дополнительные параметры, коотрые могут понадобится при обработке получаемого кэша.

        No Longer Returned:
            dict: Обработанное значение кэша для возвращения.
        """
        pass
