###############################
Абстрактный класс TicketService
###############################

.. autoclass:: third_party.ticket_service.ticket_service_abc.abc.TicketService

В дочерних классах ``TicketService`` должны быть реализованы следующие методы (наследуемые от абстрактоного класса методы отмечены как ABC):

* ``discover_schemes`` (ABC)

  .. code:: python

    [
      {
        'scheme_id': int,
        'scheme_title': str,
      }
    ]

* ``discover_groups`` (ABC)

  .. code:: python

    [
      {
        'group_id': int,
        'group_title': str,
        'group_datetime': datetime,
        'group_text': str,
        'group_min_price': Decimal,
        'scheme_id': int,
      }
    ]

* ``discover_events`` (ABC)

  .. code:: python

    [
      {
        'event_id': int,
        'event_title': str,
        'event_datetime': datetime,
        'event_text': str,
        'event_min_price': Decimal,
        'event_min_age': int,
        'group_id': int,
        'scheme_id': int,
        'promoter': str,
      }
    ]

* ``sectors``

  .. code:: python

    [
      {
        'sector_id': int,
        'sector_title': str,
      }
    ]

* ``seats_and_prices`` (ABC)

  .. code:: python

    {
      'seats': {
        'ticket_id' (str) {
          'ticket_id': str,
          'sector_id': int,
          'sector_title': str,
          'row_id': int,
          'seat_id': int,
          'seat_title': str,
          'price': Decimal,
          'price_order': int,
        }
      },
      'prices': [Decimal,],  # цены на билеты Decimal по возрастанию
      'in_progress': bool,
      'success': bool,
    }

* ``reserve`` (ABC)

  .. code:: python

    {
      'success': bool,
      'action': str,
      ...
    }

* ``ticket_status``

  .. code:: python

    {
      'success': True,
      'status': str,
    }

    {
      'success': False,
      'code': str,
      'message': str,
    }

* ``order_create`` (ABC)

  .. code:: python

    {
      'success': True,
      'order_id': int,
      'tickets': [
        {
          'ticket_uuid': str,
          'bar_code': str,
        }
      ]
    }

    {
      'success': False,
      'code': str,
      'message': str,
    }

* ``order_approve`` (ABC)

  .. code:: python

    {
      'success': True,
    }

    {
      'success': False,
      'code': str,
      'message': str,
    }

* ``order_cancel`` (ABC)

  .. code:: python

    {
      'success': True,
    }

    {
      'success': False,
      'code': str,
      'message': str,
    }

* ``order_refund`` (ABC)

  .. code:: python

    {
      'success': True,
      'amount': Decimal,
    }

    {
      'success': False,
      'code': str,
      'message': str,
    }

*******
Фабрика
*******

Необходимый в том или ином случае класс сервиса продажи билетов инстанцируется с помощью фабрики ``ticket_service_factory``.

.. automodule:: third_party.ticket_service.ticket_service_abc.factory
