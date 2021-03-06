################
Билеты в заказах
################

**************
Список билетов
**************

Фильтры
=======

* текстовый поиск по идентификатору заказа в СПБ
* текстовый поиск по реквизитам покупателя (ФИО, телефон, email)
* фильтр по статусу заказа
* фильтр по способу получения билетов
* фильтр по способу оплаты заказа
* фильтр по событию, к которому привязан заказ
* фильтр по дате и времени события
* фильтр по СПБ, к которому привязано событие

.. only:: dev

  Действия с выделенными объектами
  ================================

  * удалить (только для суперадминистраторов)

Столбцы в таблице заказов
=========================

* **Уникальный идентификатор билета**

* **ID заказа**

* **Сектор** - название сектора в СПБ.

* **Ряд** - идентфикатор ряда в СПБ.

* **Место** - название места в СПБ.

* **Цена** билета.

* **Штрих-код** билета.

В процессе оформления заказа обрботчик пытается получить штрих-код из СПБ при создании нового заказа. Если штрих-код по каким-то причинам получить не удалось - он генерируется случайным образом.

* **Сервис продажи билетов**, к которому привязано событие, в котором сдалан заказ билетов.

* **Сайт**, к которому привязано событие, в котором сдалан заказ билетов.

******************************
Страница редактирования билета
******************************

Атрибуты билета
===============

Параметры заказа
----------------

* **ID заказа** - идентификатор заказа в СПБ.

* **Сервис продажи билетов**, к которому привязано событие, в котором сдалан заказ билетов.

* **Сайт**, к которому привязано событие, в котором сдалан заказ билетов.

Параметры билета
----------------

* **Уникальный идентификатор билета** (UUID), формируемый в процессе оформления заказа.

* **ID заказа**, полученный от СПБ в процессе оформления заказа.

* **Штрих-код** билета.

* **ID сектора** - идентфикатор сектора в СПБ.

* **Сектор** - название сектора в СПБ (например, *партер* или *танцпол*).

* **ID ряда** - идентфикатор ряда в СПБ.

* **ID места** - идентфикатор места в СПБ.

* **Место** - название места в СПБ.

* **Цена** билета.

* **Сидячее место** - билет на сидячее место или билет со свободной рассадкой (например, *танцпол*, *фанзона* и т.п.).

  Статус места задаётся в схеме зала с помощью атрибута ``data-is-fixed``.

* **Пробит ли на входе** - пробит ли билет на входе на мероприятие или нет.

.. todo:: Задел на будущее - на данный момент проверка электронных билетов на входе на мероприятие не реализована.

  .. only:: dev

    Это можно сделать разными способами:

    * либо БЕЗ использования Интернета на месте - используя считыватель штрих-кодов, сохраняющий штрих-коды пробитых билетов в какой-нибудь локальный файл, из которого затем в админ-панели билеты пакетно отмечаются пробитыми;
    * либо С использованием Интернета на месте - используя считыватель штрих-кодов в связке программным интерфейсом, который сразу же отправляет информацию в бэкенд сайта и отмечает конкретный билет пробитым.
