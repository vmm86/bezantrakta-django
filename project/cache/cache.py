import decimal
import simplejson as json
from abc import ABC, abstractmethod, abstractproperty

from django.core.cache import caches
from django.core.exceptions import ObjectDoesNotExist

from project.shortcuts import debug_console, json_serializer


class ProjectCache(ABC):
    """
    Абстрактный класс-родитель конкретных классов кэширования записи какой-либо модели проекта с пред- и постобработкой.

    Attributes:
        entities (tuple): Перечень моделей или других сущностей для создания кэша (указывается в дочерних классах).
        cache_backend (string): Используемый бэкенд кэша из настроек проекта (по умолчанию - ``default``).
        key (str): Текущий ключ для создания/обновления/получения кэша.
        value (dict): Текущее обработанное значение кэша для вывода.
    """
    entities = ()
    cache_backend = 'default'
    database_first = True
    key = ''
    value = None

    def __init__(self, entity, object_id, reset=False, delete=False, **kwargs):
        """Конструктор класса.

        Args:
            entity (str): Название модели или другой сущности для создания кэша.
            object_id (int|str|uuid.UUID): Идентификатор записи в БД.
            reset (bool, optional): В любом случае пересоздать кэш, даже если он имеется.
            delete (bool, optional): Удалить кэш.
            **kwargs: Дополнительные параметры для получения кэша.

        Returns:
            dict|None: Обработанное значение кэша для вывода, если вывод требуется.
        """
        super().__init__()

        cache = caches[self.cache_backend]

        self.set_cache_key(entity, object_id, **kwargs)
        self.value = cache.get(self.key)
        debug_console('cache_key: ', self.key)

        # При явном инвалидировании кэша сначала удаляется его старое значение
        if reset or delete:
            cache.delete(self.key)
            # При явном удалении кэша работа завершается
            if delete:
                return None

        # Если кэш отсутствует или присутствует, но явно инвалидируется
        if not self.value or reset:
            # Получаем значение из БД
            if self.database_first:
                debug_console('try database...')
                try:
                    self.value = dict(self.get_object(object_id, **kwargs))
                except (ObjectDoesNotExist, TypeError):
                    if 'obj' in kwargs:
                        debug_console('nothing found in DB - trying kwargs[obj]...')
                        self.value = kwargs['obj']
                    else:
                        debug_console('nothing to save - return None')
                        return None
            # Получаем значение из входных параметров в **kwargs
            else:
                if 'obj' in kwargs:
                    debug_console('trying kwargs[obj]...')
                    self.value = kwargs['obj']
                    debug_console('self.value', str(self.value)[:200], '...', type(self.value))
                else:
                    debug_console('nothing to save - return None')
                    return None

            # При необходимости обрабатываем полученные данные
            self.cache_preprocessing(**kwargs)
            debug_console('cache_value_preprocessed:', str(self.value)[:200], '...', type(self.value))

            # Записываем полученные данные в кэш
            cache.set(self.key, json.dumps(self.value, ensure_ascii=False, default=json_serializer))
            debug_console('cache_value_set')
        else:
            # Получаем данные из имеющейся в кэше JSON-строки
            self.value = json.loads(self.value, parse_float=decimal.Decimal)
            # При необходимости обрабатываем полученные из кэша данные
            self.cache_postprocessing(**kwargs)
            debug_console('cache_value_postprocessed:', str(self.value)[:200], '...', type(self.value))

    def __str__(self):
        return '{cls}({key})'.format(
            cls=self.__class__.__name__,
            key=self.key,
        )

    def set_cache_key(self, entity, object_id, **kwargs):
        """Формирование ключа для сохранения нового или получения имеющегося кэша.

        Метод можно переопределить в дочернем классе для формирования заведомо уникального сочетания данных в ключе.

        Args:
            entity (str): Название модели или другой сущности для создания кэша.
            object_id (int|str|uuid.UUID): Идентификатор записи в БД.
            **kwargs: Дополнительные параметры, которые могут понадобится при формировании ключа для получения кэша.
        """
        self.key = '{entity}.{object_id}'.format(entity=entity, object_id=object_id)

    @abstractmethod
    def get_object(self, object_id, **kwargs):
        """Получение объекта из модели в БД или из входных параметров.

        Args:
            object_id (int|str|uuid.UUID): Идентификатор записи в БД.
            **kwargs: Дополнительные параметры, которые могут понадобится при получении данных из БД.

        Returns:
            django.db.models.query.QuerySet: Объект конкретной модели в БД.
        """
        pass

    @abstractmethod
    def cache_preprocessing(self, **kwargs):
        """Предобработка значения кэша перед его сохранением.

        Args:
            **kwargs: Дополнительные параметры, которые могут понадобится при обработке получаемого из БД значения.

        No Longer Returned:
            dict: Обработанное значение для сохранения в кэш.
        """
        pass

    @abstractmethod
    def cache_postprocessing(self, **kwargs):
        """Постобработка ранее полученного значения кэша перед его возвращением.

        Args:
            **kwargs: Дополнительные параметры, которые могут понадобится при обработке получаемого кэша.

        No Longer Returned:
            dict: Обработанное значение кэша для возвращения.
        """
        pass
