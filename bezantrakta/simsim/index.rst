#############################
Главная страница админ-панели
#############################

Заголовок любых страниц админ-панели содержит следующие элементы:

* логотип Безантракта, ведущий на главную страницу админ-панели;
* :doc:`choose_domain_or_city` (выпадающий список городов/сайтов для выбора);
* имя текущего администратора;
* ссылка для перехода на сайт;
* ссылка на эту справочную информацию;
* возможность изменить свой пароль для входа в админ-панель;
* возможность выйти из текущего сеанса.

************************
Разделы главной страницы
************************

Разделы размещены на главной странице админ-панели по степени важности для основной бизнес-задачи сайтов Безантракта - продажа билетов на зрелищные мероприятия. Важные разделы находятся вверху, сопутствующие/менее важные задачи размещены внизу. Визуально можно видеть, какие разделы являются дочерними по отношению к своим родительским разделам.

.. rst-class:: main-page-blocks

* :doc:`last_actions` всех администраторов системы в хронологическом порядке.

* **География сайтов**

  * :doc:`/bezantrakta/location/admin/city` России, в которых могут быть размещены сайты Безантракта.

    * :doc:`/bezantrakta/location/admin/domain` Безантракта, привязанные к ранее созданным городам.

* **Сервисы продажи билетов**

  * :doc:`/third_party/ticket_service/admin/ticket_service` (СПБ), подключенные к тому или иному сайту.

    * :doc:`/third_party/ticket_service/admin/ticket_service_scheme_venue_binder`

      * :doc:`/third_party/ticket_service/admin/ticket_service_scheme_sector`

* **Сервисы онлайн-оплаты**

  * :doc:`/third_party/payment_service/admin/payment_service` (СОО), подключенные к тому или иному сервису продажи билетов.

* **События**

  * :doc:`/bezantrakta/event/admin/event_venue`

    * :doc:`/third_party/ticket_service/admin/ticket_service_scheme_venue_binder`

      * :doc:`/third_party/ticket_service/admin/ticket_service_scheme_sector`

  * :doc:`/bezantrakta/event/admin/event`, импортируемые из ранее подключенных к сайту СПБ и доступные для размещения на сайте.
  * :doc:`/bezantrakta/event/admin/event_category`
  * :doc:`/bezantrakta/event/admin/event_link`
  * :doc:`/bezantrakta/event/admin/event_container`

* **Заказы**

  * :doc:`/bezantrakta/order/admin/order` билетов, сделанные в событиях, опубликованных на том или ином сайте.

    * :doc:`/bezantrakta/order/admin/order_ticket`

* **HTML-страницы**

  * :doc:`/bezantrakta/article/admin/article` для размещения на сайте, которые можно создать в визуальном редакторе.

* **Меню**

  * :doc:`/bezantrakta/menu/admin/menu`, которые можно размещать на сайте.

    * :doc:`/bezantrakta/menu/admin/menu_item`, вложенные в меню и ведущие на те ли иные страницы сайта

* **Баннеры**

  * :doc:`/bezantrakta/banner/admin/banner_group`

    * :doc:`/bezantrakta/banner/admin/banner_group_item`, вложенные в группы баннеров, которые могут вести на другие страницы (внутри сайта или на друних сайтах).

.. toctree::
  :maxdepth: 1
  :caption: События

  context_processors/index
  fields/index
