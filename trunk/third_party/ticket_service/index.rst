################################
Раздел "Сервисы продажи билетов"
################################

**Сервисы продажи билетов (СПБ)**
  Сторонние сервисы, предназначенные для продажи билетов на различные мероприятия (концерты, спектакли и т.п.).

На данный момент платформа поддерживает работу с двумя видами СПБ:

* :deleted:`СуперГовно` **СуперБилет**
* **Радарио**

.. todo:: В перспективе возможна работа с :deleted:`ПрофГовно` **ПрофТикет** и **SmartBilet**.

.. only:: dev

  Приложение ``ticket_service`` - работа со сторонними СПБ, которые хранятся в модели ``TicketService`` и могут быть подключены к одному или нескольким сайтам по внешнему ключу.

.. toctree::
  :maxdepth: 3
  :caption: Сервисы продажи билетов

  admin/ticket_service
  admin/ticket_service_scheme_venue_binder
  admin/ticket_service_scheme_sector
  ticket_service_abc/index
  ticket_service_abc/superbilet/index
  ticket_service_abc/radario/index
