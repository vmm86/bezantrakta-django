##################################
Полезные функции для всего проекта
##################################
Полезные функции для использования в разных приложениях проекта хранятся в пакете ``project.shortcuts``.

*******************************
base_template_context_processor
*******************************
Условный запуск процессора контекста для отображения афиш ТОЛЬКО в базовом шаблоне (везде, кроме шагов заказа билетов).

.. automodule:: project.shortcuts.base_template_context_processor

**************
boolean_values
**************
Значения, которые можно приводить к булеву типу данных (например, в ответе запроса к API): ``'True'``, ``'true'``, ``1``, ``'1'``, ``'y'``, ``'yes'``, ``'д'``, ``'да'``.

.. automodule:: project.shortcuts.boolean_values

******************
build_absolute_url
******************
Конструктор абсолютного URL-адреса с указанием опциональной относительной ссылки.

* Если относительная ссылка задана - получаем полную абсолютную ссылку "*протокол-домен-ссылка*".
* Если относительная ссылка НЕ задана - получаем абсолютную ссылку "*протокол-домен*" (**без слэша в конце!**). Её можно подставлять к любым относительным ссылкам **со слэшем в начале** (например, в шаблоне).

.. automodule:: project.shortcuts.build_absolute_url

************************
datetime_localize_or_utc
************************
Локализация даты/времени или приведение к UTC.

* Если в дате/времени указан часовой пояс - дата/время остаётся неизменной (сохраняется в БД в ``UTC``!).
* Если в дате/времени НЕ указан часовой пояс - дата/время локализуется с учётом часового пояса.

.. automodule:: project.shortcuts.datetime_localize_or_utc

*************
debug_console
*************
Условный вывод отладочной информации в консоль ТОЛЬКО в ``development``-окружении.

.. todo:: С полномасштабным применением тестирования в проекте от этого модуля можно будет отказаться.

.. automodule:: project.shortcuts.debug_console

*************
humanize_date
*************
Получение человекопонятной даты с русскоязычным месяцем в родительном падеже.

.. automodule:: project.shortcuts.humanize_date

***************
json_serializer
***************
Сериализация объекта в JSON с учётом специфических типов данных (``datetime.datetime``, ``uuid.UUID``).

.. automodule:: project.shortcuts.json_serializer

***************
render_messages
***************
Добавление статусных сообщений в очередь ``messages`` и их последующий вывод в шаблоне того или иного представления.

.. automodule:: project.shortcuts.render_messages

************
timezone_now
************
Получение текущей даты/времени в текущем часовом поясе.

.. automodule:: project.shortcuts.timezone_now

******
urlify
******
Переписанный на **Python** из **JavaScript** механизм генерации псевдонима ``slug`` из исходной строки. Используется в менеджмент-команде ``ticket_service.management.commands.ts_discover`` при создании псеводнимов для импортируемых из сервисов продажи билетов событий/групп на основе их названий и идентификаторов.

.. automodule:: project.shortcuts.urlify
