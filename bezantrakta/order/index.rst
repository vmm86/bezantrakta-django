Заказы
======

В этом разделе содержится информация о заказах, сделанных пользователями сайта, и билетах, входящих в эти заказы.

.. toctree::
  :maxdepth: 1
  :caption: Заказы

  admin/order
  admin/order_ticket

.. only:: dev

  Модели
  ------

  Заказы билетов
  ^^^^^^^^^^^^^^
  .. autoclass:: bezantrakta.order.models.Order

  Билеты в заказах
  ^^^^^^^^^^^^^^^^
  .. autoclass:: bezantrakta.order.models.OrderTicket

  Кэширование заказов
  -------------------
  .. autoclass:: bezantrakta.order.cache.OrderCache

  Виды
  ----

  Шаг 1 заказа билетов
  ^^^^^^^^^^^^^^^^^^^^
  Страница события и выбор билетов на схеме зала.

  .. automodule:: bezantrakta.order.views.order_step_1

  Шаг 2 заказа билетов
  ^^^^^^^^^^^^^^^^^^^^
  Ввод контактов покупателя и выбор способа доставки/оплаты билетов.

  .. automodule:: bezantrakta.order.views.order_step_2

  Шаг 3 заказа билетов
  ^^^^^^^^^^^^^^^^^^^^
  Подтверждение успешного заказа с выводом информации о нём.

  .. automodule:: bezantrakta.order.views.order_step_3
