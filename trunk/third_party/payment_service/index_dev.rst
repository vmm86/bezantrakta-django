Сервисы онлайн-оплаты
=====================
Приложение ``payment_service`` - работа со сторонними сервисами онлайн-оплаты (**Сбербанк**, **СургутНефтеГазБанк**).

Сервисы онлайн-оплаты добавляются в модели ``payment_service.PaymentService`` и могут быть подключены к одному или нескольким сервисам продажи билетов по внешнему ключу.

.. toctree::
  :maxdepth: 3
  :caption: Сервисы онлайн-оплаты

  payment_service/index
  payment_service/management/index
  payment_service/models/index
  payment_service/payment_service_abc/index
  payment_service/payment_service_abc/sberbank/index
  payment_service/payment_service_abc/sngb/index
