################################
Абстрактный класс PaymentService
################################

.. autoclass:: third_party.payment_service.payment_service_abc.abc.PaymentService

В дочерних классах ``PaymentService`` должны быть реализованы следующие методы (наследуемые от абстрактоного класса методы отмечены как ABC):

* ``payment_create`` (ABC)

  .. code:: python

    {
      'success': bool,
      'payment_url': str,
      'payment_id': str,
      'action_code': str,
      'action_message': str,
    }

* ``payment_status`` (ABC)

  .. code:: python

    {
      'success': True,
      'order_id': int,
      'payment_id': str,
      'total': Decimal,
      'is_refunded': bool,
    }

    {
      'success': False,
      'code': str,
      'message': str,
    }

* ``payment_refund`` (ABC)

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
Необходимый в том или ином случае класс сервиса онлайн-оплаты инстанцируется с помощью фабрики ``payment_service_factory``.

.. automodule:: third_party.payment_service.payment_service_abc.factory
