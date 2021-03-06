########################################
Установка и поддержка онлайн-оплаты СНГБ
########################################

*********************
Контакты техподдержки
*********************

* ecm@sngb.ru
* `(3462) 39-83-38 <tel:+73462398338>`_
* `(3462) 39-88-77 <tel:+73462398877>`_
* `(800) 775-88-04 <tel:+78007758804>`_

Работают с 7:00 до 16:00 по московскому времени (*UTC +3*).

.. seealso::

  `Документация по API <http://ecomm.sngb.ru/docs>`_.

.. warning::

  Для правильной работы с *development* или *production* средой нужно отправить в техподдрежку СНГБ сообщение с указанием IP-адреса, на котором работает *development*-сайт или *production*-сайт для его добавления в их межсетевой экран (firewall).

  *development*-IP-адрес добавляется на определённое время (*примерно на 4 месяца)*. Если по истечении этого времени снова требуется проводить тестовые оплаты - необходимо заново отправить запрос в техподдержку.

  *production*-IP-адрес добавляется бессрочно и должен быть изменён только при смене самого IP-адреса.

****************
Основные понятия
****************
.. glossary::

  **CommerceGateway**
    Cервис Интернет-эквайринга.

  **Merchant**
    Владелец Интернет-магазина (мерчант).

  **HostedPaymentPage (HPP)**
    `Платёжная форма банка <https://ecm.sngb.ru/Gateway/hppaction>`_, на которой клиент вводит данные своей банковской карты.

  **Pre-Shared Key (PSK)**
    Секретный ключ для аутентификации любых запросов к сервису оплаты (*16 символов*: латинские буквы, цифры, спецсимволы). Регистрируется в личном кабинете мерчанта.

  **Hash Type**
    Алгоритм хэширования **Pre-Shared Key** (по умолчанию **SHA-1**).

  **TrackID**
    Уникальный номер заказа в Интернет-магазине.

  **PaymentID**
    Уникальный номер оплаты (*15 цифр*, но для совместимости лучше хранить в виде строки), получаемый при создании новой оплаты. Оплата подразделяется на отдельные *транзакции*.

  **PaymentInitServlet**
    `Сервлет для инициализации новой оплаты <https://ecm.sngb.ru/Gateway/PaymentInitServlet>`_. Формирует уникальный номер оплаты **PaymentID** и URL платёжной формы **HostedPaymentPage**, на которую нужно перенаправить покупателя после успешного создания оплаты.

  **URL Init Notification**
    URL Интернет-магазина, предварительно обрабатывающий *успешный результат оплаты*.

  **URL Error**
    URL Интернет-магазина, предварительно обрабатывающий *НЕуспешный результат оплаты*.

    * *Техническая ошибка* - платёжная среда недоступна.
    * *Сетевая ошибка* - платёжная среда не может отправить Интернет-магазину ответ на страницу **URL Init Notification** и получить адрес финальной страницы **URL Result**. Покупатель направляется на страницу **URL Error** с пустыми параметрами.
    * *Неправильные данные* - Клиент ввёл неверный номер карты или недопустимые символы в поле номера.

  **TranID**
        Уникальный идентификатор каждой отдельной транзакции в процессе оплаты.

    * **AUTHORIZATION** (авторизация) - проверка карты клиента и доступности необходимых для покупки средств.
    * **CAPTURE** (подтверждение) - дальнейшая обработка оплаты.
    * **VOID** (отмена) - отмена оплаты.
    * **CREDIT** (возврат) - возврат средств на карту покупателю.

Оплата проводится с одновременной авторизацией и подтверждением при вводе клиентом данных карты (без постадийной оплаты).

Любой HTTP-запрос к API необходимо аутентифицировать с помощью хэша в параметре **udf5**.

Строка для хеширования формируется конкатенацией значений **MerchantID** + **Amount** + **TrackID** + **Action** + **PSK**.

Хэширование строки проводится по алгоритму, указанному в параметре **Hash Type** в личном кабинете Мерчанта (*SHA-1*).

*******************
Процесс подключения
*******************

- Получение от банка документации для разработчиков.
- Получение доступа к тестовой среде оплаты - регистрация Интернет-магазина в личном кабинете Мерчанта с указанием необходимых параметров:
  * **URL Init Notification**
  * **URL Tran Notification**
  * **URL Error**
  * **Pre-Shared Key** (PSK)
  * **Hash Type** (по умолчанию *SHA-1*).
- Передача банку названия домена, IP-адреса, SSL-сертификат (при его наличии) и их настройка в системе **CommerceGateway**.
- Настройка и тестирование подключения к сервису **CommerceGateway**.
- Тестирование и одобрение тестового магазина со стороны банка.
- Получение доступа к *production*-оплаты.

*******************************
Алгоритм процесса онлайн-оплаты
*******************************

- Запрос на инициализацию оплаты с помощью метода **init** со страницы ввода данных покупателя в Интернет-магазине.
  * Если запроса успешный - в ответе приходит URL платёжной формы **HostedPaymentPage** с **PaymentID**.
  * Если запрос НЕуспешный - в ответе приходит **URL Error**.
- Редирект c сайта Интернет-магазина на **HostedPaymentPage**.
- Заполнение реквизитов покупателем и оплата заказа (время сессии на оплату - ``15 минут``).
- На стороне Интернет-магазина:
  * Если оплата завершилась успешно - вызывается обработка по **URL Init Notification**.
  * Если оплата завершилась НЕуспешно - вызывается обработка по **URL Error**.
  * В любом случае требуется получить ответ с параметрами оплаты, в ответ **напечатать на экране** URL страницы Интернет-магазина (``echo`` в PHP или ``TemplateResponse`` в Django), обрабатывающей результаты платежа (URL Result), на которую СНГБ сделает *редирект*, после чего можно обработать результаты платежа на стороне Интернет-магазина и, в свою очередь, сделать редирект на страницу с результатами заказа (шаг 3 заказа билетов).
