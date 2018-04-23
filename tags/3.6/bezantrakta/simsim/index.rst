################
Главная страница
################

Заголовок любых страниц админ-панели содержит следующие элементы:

* логотип Безантракта, ведущий на главную страницу админ-панели;
* **выпадающий список городов/сайтов для выбора**;
* имя текущего администратора;
* ссылка для перехода на сайт;
* ссылка на эту справочную информацию;
* возможность изменить свой пароль для входа в админ-панель;
* возможность выйти из текущего сеанса.

Функционал выпадающего списка в заголовке подробно описан в разделе :doc:`choose_domain_or_city`.

************************
Разделы главной страницы
************************

.. rst-class:: main-page-blocks

* :doc:`last_actions` всех администраторов системы в хронологическом порядке.

* **География сайтов**

  * :doc:`../location/admin/city` России, в которых могут быть размещены сайты Безантракта.

    * :doc:`../location/admin/domain` Безантракта, привязанные к ранее созданным городам.

* **Сервисы продажи билетов**

  * :doc:`../../third_party/ticket_service/admin/ticket_service`, подключенные к тому или иному сайту.

    * :doc:`../../third_party/ticket_service/admin/ticket_service_scheme`

      * :doc:`../../third_party/ticket_service/admin/ticket_service_scheme_sector`

* **Сервисы онлайн-оплаты**

  * :doc:`../../third_party/payment_service/admin/payment_service`, подключенные к тому или иному сервису продажи билетов (если это требуется).

* **События**

  * :doc:`../event/admin/event_venue`

    * :doc:`../../third_party/ticket_service/admin/ticket_service_scheme`

      * :doc:`../../third_party/ticket_service/admin/ticket_service_scheme_sector`

  * :doc:`../event/admin/event`, импортируемые из ранее подключенных к сайту сервисов продажи билетов и доступные для размещения на сайте.
  * :doc:`../event/admin/event_category`
  * :doc:`../event/admin/event_link`
  * :doc:`../event/admin/event_container`

* **Заказы**

  * :doc:`../order/admin/order` билетов, сделанные в событиях, опубликованных на том или ином сайте.

    * :doc:`../order/admin/order_ticket`

* **HTML-страницы**

  * :doc:`../article/admin/article` для размещения на сайте, которые можно создать в визуальном редакторе.

* **Меню**

  * :doc:`../menu/admin/menu`, которые можно размещать на сайте.

    * :doc:`../menu/admin/menu_item`, вложенные в меню и ведущие на те ли иные страницы сайта

* **Баннеры**

  * :doc:`../banner/admin/banner_group`

    * :doc:`../banner/admin/banner_group_item`, вложенные в группы баннеров, которые могут вести на другие страницы (внутри сайта или на друних сайтах).

.. only:: dev

  ********************
  Процессоры контекста
  ********************

  Информация о текущем рабочем окружении для суперадминистраторов
  ===============================================================
  .. automodule:: bezantrakta.simsim.context_processors.environment

  Параметры фильтра по городу/сайту
  =================================
  .. automodule:: bezantrakta.simsim.context_processors.queryset_filter
