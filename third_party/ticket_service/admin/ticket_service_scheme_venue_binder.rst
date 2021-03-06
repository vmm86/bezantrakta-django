###########
Схемы залов
###########

*****************
Список схем залов
*****************

Фильтры
=======

* текстовый поиск по названию схемы зала и по содержимому схемы зала
* фильтр по залам (местам проведения событий), к которым привязаны схемы залов
* фильтр по сервисам продажи билетов (СПБ), из которых испортируются и к которым привязаны схемы залов

Действия с выделенными объектами
================================

* удалить
* пересоздать кэш

Столбцы в таблице схем залов
============================

* **Название схемы зала**
* **ID** - идентификатор схемы зала в СПБ.
* **Схема зала** - отрисована ли схема зала или ещё нет.
* **Секторы** - привязаны ли к схеме зала секторы (если это необходимо).
* **Сервис продажи билетов**, к которому привязаны схемы залов.

**********************************
Страница редактирования схемы зала
**********************************

Атрибуты схемы зала
===================

* **Название схемы зала**

* **ID схемы зала** в СПБ.

* **Сервис продажи билетов**, к которому привязана схема зала.

* **Зал**, к которому привязана схема зала.

Только после привязки схемы зала к залу из неё будут импортированы принадлежащие ей события в СПБ.

* **Схема зала** - редактор для отрисовки схемы зала.

Секторы в схеме зала
--------------------
В таблице выводятся все имеющиеся :doc:`секторы <ticket_service_scheme_sector>`, привязанные к конкретной схеме зала с их атрибутами:

* **Название сектора**
* **ID сектора**
* **Сектор в схеме зала** - редактор для отрисовки сектора.

********************
Отрисовка схем залов
********************

При импорте информации из СПБ *схемы залов изначально создаются пустыми*. Чтобы показать свободные для продажи места в событии на сайте, схему зала нужно нарисовать.

.. only:: dev

  У родительского элемента всей табличной схемы зала или сектора ``<table>`` обязательно указывается класс ``stagehall``. Для понимания, к какому СПБ принадлежит схема, к таблице добавляется data-атрибут ``data-ts`` с псевдонимом СПБ. В отсутствие атрибута ``data-ts`` схема зала относится к СуперБилету.

Схемы зала создаются, как правило, на основе таблиц и бывают 2-х типов:

* **обычная схема зала** (табличная), в которой содержатся места для выбора покупателем.
* **посекторная схема зала** (табличная или круговая) с активными кнопками для выбора схем отдельных секторов, которые создаются после редактирования конкретной посектрной схемы в привязке к ней.

  Схемы в СПБ не являются посекторными сами по себе (по крайней мере, такой функционал в имеющихся СПБ не реализован). Посекторную схему какого-либо зала администратор может сделать в админ-панели самостоятельно. Такую схему имеет смысл нарисовать, если зал достаточно большой и одновременное открытие всего зала сразу будет визуально неудобным для покупателя (особенно на узких экранах мобильных устройств). В этом случае:

  - Сначала **создаётся посекторная схема** (табличная или круговая);
  - Затем в посекторной схеме **добавляются/редактируются активные кнопки**, нажимая на которые, покупатель будет открывать схему каждого из секторов;
  - После этого в привязке к посекторной схеме **создаются схемы всех относящихся к этой схеме секторов**.

Для редактирования схем предназначена нижняя панель в тулбаре HTML-редактора. Она состоит из нескольких групп кнопок, разделёных вертикальными чертами. Порядок следования групп кнопок слева направо обозначает и порядок работы с каждой новой схемой:

- Сначала нужно создать новую заготовку схемы зала для последующего редактирования.

  * |init_table| - Создать новую табличную схему зала (чтобы сделать её затем обычной или посекторной);
  * |init_circle| - Создать новую круговую посекторную схему зала.

  Для обычной схемы зала создайте таблицу с необходимым числом строк и столбцов. Если в схеме должны быть **только стоячие места** (БЕЗ фиксированной рассадки) - создайте таблицу с одним столбцом и необходимым числом строк (в одной строке - подпись названия сектора |sector|, в следующей - список стоячих мест в этом секторе |nofixedseats|).

  Для посекторной схемы зала:

  - создайте табличную |init_table| (для прямоугольных залов) или круговую |init_circle| (для круглых залов типа цирка) схему,
  - затем добавьте в ней активные кнопки для выбора секторов |sectorbuttonactive|,
  - после чего создайте в привязке к ней схемы всех необходимых секторов. В самих схемах секторов НЕ нужно указывать название сектора - при выводе на сайте название подставляется автоматически из поля "*Название сектора*".

  .. note:: В редакторе круговой посекторной схемы **НЕ показывается круговой манеж в центре сцены**, но при этом **в самой схеме он присутствует и будет выводиться на сайте**. Это вынужденная мера, т.к. круговой манеж при открытии редактора неправильно позиционируется (уезжает на край схемы, а не остаётся в центре).

  .. attention:: Будьте внимательны! При повторном выполнении этих команд **в любом случае будет создана новая пустая схема**, даже если схема уже была добавлена и отредактирована ранее! **Сохраняйте промежуточные изменения**, чтобы не потерять сделанную работу.

- Кнопки для редактирования табличной схемы.

  * |tablerowinsertbefore| - Вставить строку выше;
  * |tablerowinsertafter| - Вставить строку ниже;
  * |tablerowdelete| - Удалить строку;
  * |tablecolumninsertbefore| - Вставить столбец слева;
  * |tablecolumninsertafter| - Вставить столбец справа;
  * |tablecolumndelete| - Удалить столбец;
  * |tablecellsmerge| - Объединить выделенные ячейки;
  * |tablecellsclear| - Очистить форматирование выделенного фрагмента.

- Толстые границы ячеек в табличной схеме.

  * |borderleft| - Левая граница ячейки;
  * |bordertop| - Верхняя граница ячейки;
  * |borderright| - Правая граница ячейки;
  * |borderbottom| - Нижняя граница ячейки.

  Если необходимо визуально разграничить какую-то часть схемы - ячейкам нужно задать *толстые границы*. Повторное нажатие на эти кнопки для конкретных ячеек отменяет сделанные изменения.

- Отметить ячейку таблицы как сцену или как название сектора/номер ряда.

  .. only:: dev

    Для специфических элементов схемы указываются соответствующие классы:

    * ``stage`` - сцена/экран/барная стойка/...;
    * ``sector`` - название сектора/номер ряда/прочие подписи.

  * |stage| - Текущая ячейка (в которой установлен курсор) отмечается как **сцена**. Текст "*Сцена*" в ячейке можно менять как угодно. Таким образом можно обозначать большие экраны рядом со сценой (Event Hall, Воронеж), барные стойки в клубах - любые значительные и важные для схемы элементы зала. Как правило, для этого потребуется объединить несколько ячеек таблицы |tablecellsmerge|.
  * |sector| - Текущая ячейка (в которой установлен курсор) или несколько выделенных ячеек отмечаются как **название сектора** или **номер ряда**. Кроме того, так можно стилизовать любые подписи, которые на схеме должны быть сделаны жирным шрифтом.

  Повторное нажатие на эти кнопки для конкретных ячеек отменяет сделанные изменения.

- Добавить сидячие или стоячие места.

  * |fixedseats| - Редактор сидячих мест.

    Сидячие места в схеме зала или сектора создаются в ячейках таблицы. Чтобы добавить несколько сидячих мест в одном ряду, нужно выделить необходимое число ячеек в табличной схеме (по горизонтали или по вертикали) и нажать на кнопку |fixedseats|. Откроется редактор сидячих мест, в котором нужно будет указать необходимые параметры места, с которого начнётся отсчёт при заполнении мест, и выбрать направление их заполнения (``слева направо/сверху вниз`` или ``справа налево/снизу вверх``). В поля для удобства подставляются введённые ранее значения. Выделенные ячейки таблицы будут последовательно заполнены местами согласно введённым настройкам:

      * Для СуперБилета нужно указывать *ID сектора*, *ID ряда* и *ID места* (ID места совпадает с его номером, который отображается в схеме зала для покупателя).
      * Для Радарио нужно указывать *ID места* и *номер места* (ID места НЕ совпадает с его номером).

    Затем при установке курсора в отдельную ячейку какого-либо места и нажатии на кнопку |fixedseats| можно будет отредактировать параметры этого конкретного места. В поля подставляются параметры текущего места.

  .. only:: dev

    Кликабельным местам на схеме зала присваиваются классы ``seat``. Для привязки информации о каждом месте, получаемой из СПБ, к схеме, каждое место содержит  обязательный атрибут ``data-ticket-id``, содержащий **идентификатор билета**. Идентификатор билета конструируется, исходя из того, какие параметры места в конкретном СПБ позволяют сформировать *уникальный идентификатор места*:

      * в СуперБилет - сочетание *ID сектора*, *ID ряда* и *ID места* (например, ``509_1_5``).
      * в Радарио - только *ID места* (например, ``18``).

    Остальные ``data``-атрибуты (в первую очередь **цена**) подгружаются к каждому доступному для заказа месту при периодическом обновлении схемы зала на шаге 1 заказа билетов.

  * |nofixedseats| - Редактор стоячих мест.

    Стоячие места в схеме зала или сектора создаются в виде списка, находящегося в одной ячейке таблицы:

    * Если в схеме должны быть **и сидячие, и стоячие места**, нужно объединить несколько ячеек в строке таблицы и добавить ряд стоячих мест в эту ячейку.
    * Если в схеме должны быть **только стоячие места**, создаётся таблица с одним столбцом и нужным числом строк (в одной строке - подпись названия сектора |sector|, в следующей - список стоячих мест в этом секторе |nofixedseats|)

    Чтобы добавить список стоячих мест в одном ряду, нужно поставить курсор в пустую ячейку табличной схемы и нажать на кнопку |nofixedseats|. Откроется редактор стоячих мест, в котором нужно будет указать необходимые параметры начального и конечного мест при их заполнении. В поля для удобства подставляются введённые ранее значения. Текущая ячейка таблицы будет заполнена списком стоячих мест согласно введённым настройкам:

      * Для СуперБилета нужно указывать *ID сектора*, *ID ряда*, *ID начального места* и *ID конечного места* в ряду (ID места совпадает с его номером).
      * Для Радарио нужно указывать *ID места* и *номер места* (ID места НЕ совпадает с его номером).

    Затем при установке курсора на какое-то место в созданном ранее списке стоячих мест и нажатии на кнопку |nofixedseats| можно будет отредактировать параметры этого конкретного списка стоячих мест (чтобы, например, увеличить иил уменьшить число стоячих мест в списке). В поля подставляются параметры текущего списка стоячих мест.

    Номера для стоячих мест не имеют значения, т.к. это места со свободным расположением зрителей. Их номера не выводятся на схеме зала, а в корзине заказа на сайте и в email-уведомлениях стоячие места указываются как **название сектора, цена** (без указания ID ряда и номера места, которые в этом случае не имеют значения).

  .. only:: dev

    Сидячие места создаются пунктами ``<li>`` маркированных списков ``<ul>`` с классом ``no-fixed-seats``. При наличии этого класса у списка все места внутри него при загрузке схемы зала автоматически получают атрибут ``data-is-fixed`` со значением ``true`` и становятся сидячими местами (местами БЕЗ фиксированной рассадки).

    Если в настройках СПБ указана опция ``hide_sold_non_fixed_seats`` со значением ``true``, тогда после загрузки страницы события на шаге 1 заказа билетов *видимыми останутся только свободные для продажи сидячие места*, а оставшиеся без возможности продажи места будут скрыты.

    Если в СПБ у стоячих мест нет уникальных идентификаторов (Радарио), в схеме зала создаётся необходимое количество мест, у которых ID билета нумеруется по порядку, начиная с ``1``.

- Добавить в посекторную схему активные или НЕактивные кнопки.

  * |sectorbuttonactive| - Активная кнопка для выбора сектора (с подписью иди без неё).

    Активные кнопки (с жёлтым фоном) в посекторной схеме нужны *для выбора схем отдельных секторов покупателем*.

  * |sectorbuttonpassive| - НЕактивная кнопка (с подписью иди без неё).

    НЕактивные кнопки (с серым фоном) в посекторной схеме могут понадобится, чтобы *создать подпись для какой-то части зала БЕЗ возможности выбора сектора* (например, подпись сектора, у которого в этой конкретной схеме нет мест), либо чтобы *создать визуальную заглушку без подписи*.

  .. only:: dev

    Элемент с классом ``sector`` (ячейка таблицы или пункт списка как сегмент круговой схемы) должен содержать тег ``<div>`` с классом ``sector-button``, а внутри него - радиокнопку (``<input>`` с атрибутами ``type="radio"`` и ``name="sectors"``) с идентификатором ``sector-NNN`` и привязанный к ней ``<label>`` c атрибутом ``for="sector-NNN"``, содержащий внутри себя ``<span>`` (с подписью названия сектора или без неё). ``NNN`` - это идентификатор схемы конкретного сектора в базе данных сайта. У НЕактивной кнопки радиокнопка отсутстувует.

  Если нужно создать круговую посекторную схему |init_circle|, активные кнопки для секторов создаются заранее.

  Если нужно создать табличную посекторную схему |init_table|, после создания таблицы нужно поместить курсор в нужную ячейку и нажать на кнопку |sectorbuttonactive| или |sectorbuttonpassive|. Откроется один и тот же редактор кнопки с двумя вкладками - он будет работать в зависимости от того, какая вкладка выбрана при редактировании. В выбранной вкладке нужно указать подпись (может быть пустой) и идентификатор схемы сектора (для активной кнопки). Для табличных посекторных схем также в любом случае нужно указывать высоту ячейки в условных единицах (``rem``) для одинакового отображения кнопок в разных браузерах.

  В любом случае любую кнопку можно изменить с активной на НЕактивную и наоборот - в редакторе кнопок нужно переключиться с одной вкладки на другую и подтвердить изменения.

  При создании схем отдельных секторов для посекторной схемы зала **идентификаторы схем секторов указываются произвольно** и могут НЕ совпадать с ID конкретного сектора в сервисе продажи билетов.

  Например, при создании круговой посекторной схемы зала её секторам присываиваются идентификаторы от 1 до указанного числа сегментов круга. Нужно создать для неё схемы секторов с указанными идентификаторами.

  Если места с одним и тем же ID сектора в сервисе продажи билетов визуально разбиты на несколько отдельных групп мест (Зелёный театр, Воронеж) - нужно создать для этих разных групп мест отдельные схемы секторов с похожими идентификаторами (например, места с ID сектора ``123`` будут хранится в схемах секторов с идентификаторами ``1231``, ``1232`` и ``1233``.

.. Включения ссылок на иконки из панели редактирования схем

.. |init_table| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/init_table.png
.. |init_circle| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/init_circle.png

.. |tablerowinsertafter| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablerowinsertafter.png
.. |tablerowinsertbefore| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablerowinsertbefore.png
.. |tablerowdelete| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablerowdelete.png
.. |tablecolumninsertafter| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecolumninsertafter.png
.. |tablecolumninsertbefore| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecolumninsertbefore.png
.. |tablecolumndelete| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecolumndelete.png
.. |tablecellsmerge| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecellsmerge.png
.. |tablecellsclear| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecellsclear.png

.. |bordertop| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/bordertop.png
.. |borderright| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/borderright.png
.. |borderbottom| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/borderbottom.png
.. |borderleft| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/borderleft.png

.. |fixedseats| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/fixedseats.png
.. |nofixedseats| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/nofixedseats.png

.. |stage| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/stage.png
.. |sector| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sector.png

.. |sectorbuttonactive| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sectorbuttonactive.png
.. |sectorbuttonpassive| image:: /bezantrakta/simsim/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sectorbuttonpassive.png
