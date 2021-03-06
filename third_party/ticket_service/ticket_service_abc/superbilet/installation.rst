################################
Установка и поддержка СуперБилет
################################

Уёбищное говнище, написаное криворукими долбоёбами. m( Разработчик - **TОНЛАЙН**.

*********************
Контакты техподдержки
*********************

* http://tonline.su
* office@tonline.su
* `(495)449-13-13 <tel:+74954491313>`_
* `(495)449-13-12 <tel:+74954491312>`_

Работают с 10:00 до 17:00 по московскому времени (*UTC +3*).

****************
Основные понятия
****************

* Место проведения - Театр, в котором проходит мероприятие (пример: «Театр Моссовета»).
* Зал места проведения - Сцена театра, в котором проходит мероприятие (пример: «Основная сцена»).
* Мероприятие - Спектакль, концерт, балет и т.д. проходящие в театре.
* Событие (единица репертуара) - Спектакль (концерт, балет и т.д.) проводимый в определенное время на определенной сцене театра.
* Сектор - Определенная часть зрительного зала (пример: Партер, Балкон, Бельэтаж).
* Предварительное бронирование - Установка специального статуса для места (или мест), свидетельствующего о том, что место (места) находятся в работе, и остальные пользователи не могут их использовать.
* Сессия - Идентификатор сессии. Как правило, используется ID сессии вебсервера. Данный параметр необходим, чтобы шлюз мог отличать соединения. Места объединяются в один заказ в рамках сессии.
* Ряд - Ряд передается строкой (макс. длина 4 символа), т.к. встречаются литерные ряды (пример: А, B, C).
* Место - Место передается строкой (макс. длина 4 символа), т.к. встречаются литерные места (пример: 1А, 2B, 3C).
* Транзакция - Идентификатор транзакции, передаваемой платежной системой. В дальнейшем по этому номеру можно отследить прохождение оплаты и т.д.
* Дата и время оплаты - Дата и время прихода извещения платежной системы об оплате.

****************************************
Схема взаимодействия сайтов с СуперБилет
****************************************

БД сайта <-> экземпляр класса SuperBilet <-> приложение zeep <-> Apache <-> STicketGate.exe <-> БД MS SQL Server Express

************************
Настройка сервера Apache
************************

Исполняемые файлы шлюзов ``STicketGate.exe`` работают на сервере Apache 2.4 как cgi-приложения.

Для избавления от ошибки с провисающими запросами к Apache в его конфигурации ``httpd.conf`` нужно указать следующие параметры:

.. code-block:: apache

  AcceptFilter http none
  AcceptFilter https none
  EnableSendfile off
  EnableMMAP off

************************
Настройка Интернет-шлюза
************************

- Cкопировать файлы ``STicketGate.exe`` и ``STicketGate.ini`` в папку ``cgi-bin``.

- Отредактировать STicketGate.ini:

.. code-block:: ini

  ; Имя сервера\инстанс
  Server=SERVER\SQL2008
  ; Имя БД
  DBName=KULTORG
  ; Тип СуперБилета (0 - Театр, 1 - Агентство)
  isTicketAgency=0
  ; Остальные параметры - константы:
  ; Шифровка пароля (0 - нет, 1 - да)
  NewPassType=1
  ; Время сброса предварительного бронирования в минутах
  MinToDropSel=15
  ; Ведение лога (0 - только ошибки, 1 - подробное логирование)
  FullReqLog=1

В программе "СуперБилет" создать пользователя шлюза (меню "Администрирование" > "Пользователи" > "Создать пользователя").
У пользователя должен стоять галочка "Пользователь для шлюза" ("Сайт своего театра/организации").
