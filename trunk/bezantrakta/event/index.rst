################
Раздел "События"
################

В этом разделе содержится информация о событиях, импортируемых из подключенных к сайтам сервисов по продаже билетов, и связанных с ними разделах.

Поскольку схемы залов привязаны, с одной стороны, к :doc:`сервисам продажи билетов <../../third_party/ticket_service/admin/ticket_service>` (СПБ), из которых они импортируются в базу данных сайта, с другой стороны, к :doc:`залам (местам проведения событий) <admin/event_venue>`, в обоих этих разделах указаны дочерние ссылки на :doc:`схемы залов <../../third_party/ticket_service/admin/ticket_service_scheme_venue_binder>` и :doc:`секторы в схемах залов <../../third_party/ticket_service/admin/ticket_service_scheme_sector>`.

.. toctree::
  :maxdepth: 1
  :caption: События

  admin/event_venue
  admin/event
  admin/event_category
  admin/event_link
  admin/event_container
