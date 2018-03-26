Полезные функции для всего проекта
==================================
Полезные функции для использования в разных приложениях проекта хранятся в пакете ``shortcuts``.

base_template_context_processor
-------------------------------
Условный запуск процессора контекста для отображения ТОЛЬКО в базовом шаблоне (везде, кроме процесса заказа билетов).

.. automodule:: project.shortcuts.base_template_context_processor

boolean_values
--------------
Значения, которые можно приводить к булеву типу данных (например, в ответе запроса к API).

.. automodule:: project.shortcuts.boolean_values

build_absolute_url
------------------
Конструктор абсолютного URL-адреса с указанием опциональной относительной ссылки.

.. automodule:: project.shortcuts.build_absolute_url

datetime_localize_or_utc
------------------------
Локализация даты/времени или приведение к UTC.

.. automodule:: project.shortcuts.datetime_localize_or_utc

debug_console
-------------
Вывод отладочной информации в консоль ТОЛЬКО в ``development``-окружении.

.. automodule:: project.shortcuts.debug_console

humanize_date
-------------
Получение человекопонятной даты с русскоязычным месяцем в родительном падеже.

.. automodule:: project.shortcuts.humanize_date

json_serializer
---------------
Сериализация объекта в JSON с учётом специфических типов данных (``datetime.datetime``, ``uuid.UUID``).

.. automodule:: project.shortcuts.json_serializer

render_messages
---------------
Добавление статусных сообщений в очередь ``messages`` и их последующий вывод в шаблоне того или иного вида.

.. automodule:: project.shortcuts.render_messages

timezone_now
------------
Получение текущей даты/времени в текущем часовом поясе.

.. automodule:: project.shortcuts.timezone_now

urlify
------
Переписанный на **Python** из **JavaScript** механизм генерации псевдонима ``slug`` из исходной строки.

Используется в менеджмент-команде ``ticket_service.management.commands.ts_discover`` при создании псеводнимов для импортируемых из сервисов продажи билетов событий/групп на основе их названий и идентификаторов.

.. automodule:: project.shortcuts.urlify
