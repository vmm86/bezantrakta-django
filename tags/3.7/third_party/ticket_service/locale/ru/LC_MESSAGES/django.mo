��    '      T  5   �      `     a  (   d  $   �  -   �  1   �          +     9     N     _     w     �     �     �     �     �          "     1  /   K  *   {      �      �  *   �  2     5   F     |     �  *   �  %   �  /     -   7  4   e  :   �     �  .   �  )   $  )   N  �  x     n
  W   q
  _   �
     )     6  �  J  *   %     ?%     H%     c%  &   t%     �%     �%  *   �%     �%     &     &  ,   ,&  #   Y&  A   }&     �&     �&  #   �&  �  '     �)     �)  %   �)     *     $*     +*  pD  ?*  *   �n     �n  $   �n     o  9   -o     go     {o                 #      $   !         	       %                                           &      "                                
                    '                                  ID event_admin_activate_or_deactivate_items ticket_service_admin_batch_set_cache ticket_service_admin_is_payment_service_added ticket_service_admin_ticket_service_schemes_count ticket_service_help_text ticketservice ticketservice_domain ticketservice_id ticketservice_is_active ticketservice_payment_service ticketservice_schemes ticketservice_settings ticketservice_slug ticketservice_slug_radario ticketservice_slug_superbilet ticketservice_title ticketservices ticketserviceschemesector ticketserviceschemesector_admin_batch_set_cache ticketserviceschemesector_if_sector_exists ticketserviceschemesector_scheme ticketserviceschemesector_sector ticketserviceschemesector_sector_help_text ticketserviceschemesector_ticket_service_sector_id ticketserviceschemesector_ticket_service_sector_title ticketserviceschemesectors ticketserviceschemevenuebinder ticketserviceschemevenuebinder_event_venue ticketserviceschemevenuebinder_scheme ticketserviceschemevenuebinder_scheme_help_text ticketserviceschemevenuebinder_ticket_service ticketserviceschemevenuebinder_ticket_service_scheme ticketserviceschemevenuebinder_ticket_service_scheme_title ticketserviceschemevenuebinders ticketservicevenuebinder_admin_batch_set_cache ticketservicevenuebinder_if_scheme_exists ticketservicevenuebinder_if_sectors_exist Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2018-02-20 09:03+0000
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3);
 ID Включить или отключить сервисы продажи билетов Пересоздать кэш выбранных сервисов продажи билетов Оплата Схем залов <ul><li><strong>init</strong> { словарь 'ключ': 'значение' } - параметры для подключения (зависят от конкретного сервиса продажи билетов):<ul><li><strong>СуперБилет</strong><ul><li><strong>host</strong> строка - URL для отправки запросов к API,</li><li><strong>user</strong> строка - имя пользователя API,</li><li><strong>pswd</strong> строка - пароль пользователя API,</li><li><strong>mode</strong> строка - режим работы API (<em>agency</em> - Агентство, <em>theatre</em> - Театр).</li></ul></li><li><strong>Радарио</strong><ul><li><strong>api_id</strong> число - идентификатор доступа к API,</li><li><strong>api_key</strong> строка - ключ доступа к API,</li><li><strong>city_id</strong> число - идентификатор города в БД Радарио, в котором находится организатор,</li><li><strong>company_id</strong> число - идентификатор организатора в БД Радарио,</li><li><strong>company_title</strong> строка - название организатора в БД Радарио.</li></ul></li></ul></li><li><strong>schemes</strong> [ список чисел ] - список идентификаторов схем залов в сервисе продажи билетов.<br>При импорте информации из сервиса продажи билетов:<ul><li>Если список НЕпустой - будут импортироваться только те залы, идентификаторы которых указаны в этом списке;</li><li>Если список пустой - будут импортироваться ВСЕ залы.</li></ul></li><li><strong>order</strong> { словарь 'ключ': 'значение' } - включение/выключение способов заказа билетов на сайте (<em>true</em> - включено, <em>false</em> - отключено):<ul><li><strong>self_cash</strong> логическое значение - получение в кассе (оффлайн-оплата),</li><li><strong>courier_cash</strong> логическое значение - доставка курьером (оффлайн-оплата),</li><li><strong>self_online</strong> логическое значение - получение в кассе (онлайн-оплата),</li><li><strong>email_online</strong> логическое значение - электронный билет на email (онлайн-оплата).</li></ul></li><li><strong>order_description</strong> { словарь 'ключ': 'значение' } - сопроводительный текст к способам заказа билетов - на шаге 2 заказа билетов и в email-уведомлении покупателю (строка, возможно с HTML-кодом):<ul><li><strong>self_cash</strong> строка - получение в кассе (оффлайн-оплата),</li><li><strong>courier_cash</strong> строка - доставка курьером (оффлайн-оплата),</li><li><strong>self_online</strong> строка - получение в кассе (онлайн-оплата),</li><li><strong>email_online</strong> строка - электронный билет на email (онлайн-оплата).</li></ul></li><li><strong>order_email</strong> { словарь 'ключ': 'значение' } - электронная почта для отправки сообщений администратору и покупателю:<ul><li><strong>user</strong> строка - логин (например, <em>zakaz@bezantrakta.ru</em>),</li><li><strong>pswd</strong> строка - пароль.</li></ul></li><li><strong>order_email_description</strong> { словарь 'ключ': 'значение' } - сопроводительный текст к способам заказа билетов в email-сообщении покупателю (строка с HTML-кодом):<ul><li><strong>self_cash</strong> строка - получение в кассе (оффлайн-оплата),</li><li><strong>courier_cash</strong> строка - доставка курьером (оффлайн-оплата),</li><li><strong>self_online</strong> строка - получение в кассе (онлайн-оплата),</li><li><strong>email_online</strong> строка - электронный билет на email (онлайн-оплата).</li></ul></li><li><strong>max_seats_per_order</strong> число - максимальное число билетов в заказе (по умолчанию - 7).</li><li><strong>courier_price</strong> число - стоимость доставки курьером в рублях (если <em>0</em> - доставка бесплатная).</li><li><strong>promoter</strong> строка - организатор мероприятий (промоутер) по умолчанию для всех событий в этом сервисе продажи билетов (подставляется в событии, если это поле в нём пустое).</li><li><strong>seller</strong> строка - продавец билетов (агент) по умолчанию для всех событий в этом сервисе продажи билетов.</li><li><strong>heartbeat_timeout</strong> число - время в секундах, по истечении которого вновь запрашивается список доступных к продаже мест на схеме зала (по умолчанию - <em>10</em>).</li><li><strong>seat_timeout</strong> число - время в минутах, по истечении которого автоматически снимается предварительный резерв мест на схеме зала (по умолчанию - <em>15</em>).</li><li><strong>hide_sold_non_fixed_seats</strong> логическое значение - возможность скрывать на схеме зала проданные места в секторах без фиксированной рассадки - маркированные списки <em>ul</em> с классом <em>non_fixed_seats</em> (по умолчанию - <em>false</em>).</li></ul> сервис продажи билетов Сайт Идентификатор Работает Сервис онлайн-оплаты Схемы залов Настройки в JSON Сервис продажи билетов Радарио СуперБилет Название сервисы продажи билетов сектор в схеме зала Пересоздать кэш выбранных секторов Сектор Схема зала Сектор в схеме зала <p>Схемы секторов создаются аналогично схеме зала.<br>Общая схема зала для работы с секторами должна содержать активные кнопки для открытия схем секторов по клику в отдельном блоке под общей посекторной схемой зала. При клике на какой-либо активной кнопке сектора в посекторной схеме зала схема выбранного сектора становится видимой, а схемы всех остальных секторов скрываются. ID сектора Название сектора секторы в схеме зала схема зала Зал Схема зала <p>При импорте информации из сервисов продажи билетов схемы залов изначально создаются пустыми. Чтобы показать свободные для продажи места в событии на сайте, схему зала нужно нарисовать.</p><p>Схемы зала создаются, как правило, на основе таблиц и бывают 2-х типов:</p><ul><li><strong>обычная схема зала</strong> (табличная), в которой содержатся места для выбора покупателем.</li><li><strong>посекторная схема зала</strong> (табличная или круговая) с активными кнопками для выбора схем отдельных секторов, которые добавляются отдельно в привязке к конкретной посекторной схеме.</li></ul><p>Посекторную схему имеет смысл создавать, если зал достаточно большой и одновременное открытие всего зала сразу визуально неудобно для покупателя (особенно на узких экранах мобильных устройств).</p><p>В этом случае:</p><ol><li>Сначала <strong>создаётся посекторная схема</strong> (табличная или круговая),</li><li>Затем в посекторной схеме <strong>добавляются/редактируются активные кнопки</strong>, нажимая на которые, покупатель будет открывать схему каждого из секторов.</li><li>После этого в привязке к посекторной схеме <strong>создаются схемы всех относящихся к ней секторов</strong>.</li></ol><p>Для редактирования схем предназначена нижняя панель в тулбаре HTML-редактора.</p> <p>Панель для редактирования схем состоит из нескольких групп кнопок, разделёных вертикальными чертами:<ol><li>Создание новой заготовки схемы зала для последующего редактирования.<ul><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/init_table.png" width="16" height="16"> - Создать новую табличную схему зала (обычная или посекторная)</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/init_circle.png" width="16" height="16"> - Создать новую круговую посекторную схему зала</li></ul><p>Для обычной схемы зала создайте таблицу с необходимым числом строк и столбцов. Если в схеме должны быть <strong>только стоячие места</strong> (БЕЗ фиксированной рассадки) - создайте таблицу с одним столбцом и необходимым числом строк (в одной строке - подпись названия сектора  <img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sector.png" width="16" height="16">, в следующей - список стоячих мест в этом секторе <img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/nofixedseats.png" width="16" height="16">).</p><p>Для посекторной схемы зала создайте табличную (для прямоугольных залов) или круговую (для круглых залов типа цирка) схему, затем добавьте в ней активные кнопки для выбора секторов, после чего создайте в привязке к ней схемы всех необходимых секторов. В самих схемах секторов НЕ нужно указывать название сектора - при выводе на сайте название подставляется автоматически из поля "Название сектора".</p></li><p>Будьте внимательны! При повторном выполнении этих команд <strong style="color: red;">в любом случае создана новая пустая схема</strong>, даже если схема уже была добавлена и отредактирована ранее! <strong>Сохраняйте промежуточные изменения</strong>, чтобы не потерять сделанную работу.</p><li>Кнопки для редактирования табличной схемы. <ul><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablerowinsertbefore.png" width="16" height="16"> - Вставить строку выше</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablerowinsertafter.png" width="16" height="16"> - Вставить строку ниже</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablerowdelete.png" width="16" height="16"> - Удалить строку</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecolumninsertbefore.png" width="16" height="16"> - Вставить столбец слева</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecolumninsertafter.png" width="16" height="16"> - Вставить столбец справа</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecolumndelete.png" width="16" height="16"> - Удалить столбец</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecellsmerge.png" width="16" height="16"> - Объединить выделенные ячейки</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecellsclear.png" width="16" height="16"> - Очистить форматирование выделенного фрагмента</li></ul></li><li>Толстые границы ячеек в табличной схеме (если необходимо визуально разграничить какую-то часть схемы). <ul><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/borderleft.png" width="16" height="16"> - Левая граница ячейки</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/bordertop.png" width="16" height="16"> - Верхняя граница ячейки</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/borderright.png" width="16" height="16"> - Правая граница ячейки</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/borderbottom.png" width="16" height="16"> - Нижняя граница ячейки</li></ul></li><p>Повторное нажатие на эти кнопки для конкретных ячеек отменяет сделанные изменения.</p><li>Отметить ячейку табличной схемы как сцену или как название сектора/номер ряда. <ul><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/stage.png" width="16" height="16"> - Отметить текущую ячейку (в которой установлен курсор) как сцену. Текст "Сцена" можно менять как угодно - так можно обозначать большие экраны рядом со сценой (Event Hall, Воронеж), барные стойки в клубах - любые значительные и важные для схемы элементы зала. Как правило, для этого потребуется объединить несколько ячеек таблицы <img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/tablecellsmerge.png" width="16" height="16">.</li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sector.png" width="16" height="16"> - Отметить текущую ячейку (в которой установлен курсор) или несколько выделенных ячеек как название сектора или номер ряда. Кроме того, так можно стилизовать любые подписи, которые должны быть сделаны жирным шрифтом.</li></ul></li><p>Повторное нажатие на эти кнопки для конкретных ячеек отменяет сделанные изменения.</p><li>Добавить сидячие или стоячие места. <ul><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/fixedseats.png" width="16" height="16"> - Редактор сидячих мест<p>Чтобы добавить несколько сидячих мест в одном ряду, нужно выделить необходимое число ячеек в табличной схеме (по горизонтали или по вертикали) и нажать на эту кнопку. Откроется редактор сидячих мест, в котором нужно будет указать необходимые параметры мест и выбрать направление их заполнения (<em>слева направо/сверху вниз</em> или <em>справа налево/снизу вверх</em>). В поля для удобства подставляются введённые ранее значения. Выделенные ячейки таблицы будут последовательно заполнены местами согласно введённым настройкам.<p><ul><li>Для СуперБилета нужно указывать ID сектора, ID ряда и ID места. При этом ID места совпадает с его номером (номер места в ячейке таблицы, который отображается в схеме зала для покупателя).</li><li>Для Радарио нужно указывать ID места и его номер, т.к. ID места в случае Радарио не совпадает с его номером.</li></ul><p>Затем при установке курсора в отдельную ячейку какого-либо места и открытии редактора сидячих мест можно редактировать параметры этого конкретного места. В поля подставляются параметры текущего места.</p></li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/nofixedseats.png" width="16" height="16"> - Редактор стоячих мест<p>Чтобы добавить список стоячих мест в одном ряду, нужно поставить курсор в пустую ячейку табличной схемы и нажать на эту кнопку. Откроется редактор стоячих мест, в котором нужно будет указать необходимые параметры мест.</p><ul><li>Для СуперБилета нужно указывать ID сектора, ID ряда, ID начального и конечного места в ряду.</li><li>Для Радарио нужно указывать ID места и его номер, т.к. ID места в случае Радарио не совпадает с его номером.</li></ul><p>Затем при установке курсора на какое-то место в созданном ранее списке и открытии редактора стоячих мест можно редактировать параметры этого конкретного списка стоячих мест. В поля подставляются параметры текущего списка стоячих мест.</p><p>Номера для стоячих мест не имеют значения, т.к. в этом нет смысла - это места со свободным распложением зрителей. Их номера не выводятся на схеме зала, а в корзине заказа на сайте и в email-уведомлениях стоячие места указываются как <strong>название сектора, цена</strong> (без указания ID ряда и номера места, которые в этом случае не имеют значения).</p></li></ul></li><li>Добавить в посекторную схему активные или НЕактивные кнопки. <ul><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sectorbuttonactive.png" width="16" height="16"> - Активная кнопка для выбора сектора<p>Активные кнопки (с жёлтым фоном) в посекторной схеме нужны для выбора схем отдельных секторов покупателем.</p></li><li><img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sectorbuttonpassive.png" width="16" height="16"> - НЕактивная кнопка (с подписью иди без неё)<p>НЕактивные кнопки (с серым фоном) в посекторной схеме могут понадобится, чтобы создать подпись для какой-то части зала БЕЗ возможности выбора сектора (например, подпись сектора, у которого в этой конкретной схеме нет мест), либо чтобы создать визуальную заглушку без подписи.</p></li></ul><p>При создании круговой посекторной схемы активные кнопки для секторов создаются заранее. Любую из них можно измнеить на НЕактивную и наоборот - редактор кнопок это позволяет.</p><p>Чтобы создать активную или НЕактивную кнопку в табличной посекторной схеме, нужно поместить курсор в нужную ячейку и нажать на кнопку <img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sectorbuttonactive.png" width="16" height="16"> или <img src="/static/ckeditor/ckeditor/plugins/bezantrakta_scheme/icons/sectorbuttonpassive.png" width="16" height="16">. Откроется один и тот же редактор кнопки с двумя вкладками - он будет работать в зависимости от того, какая вкладка выбрана для редактирования. В выбранной вкладке нужно указать подпись (может быть пустой) и идентификатор схемы сектора для активной кнопки. Для табличных посекторных схем также в любом случае нужно указывать высоту ячейки в условных единицах (<em>rem</em>) для одинакового отображения кнопок в разных браузерах.</p><p>При создании схем отдельных секторов для посекторной схемы зала <strong>идентификаторы схем секторов указываются произвольно</strong> и могут НЕ совпадать с ID конкретного сектора в сервисе продажи билетов.</p><p>Например, при создании круговой посекторной схемы зала её секторам присываиваются идентификаторы от 1 до указанного числа сегментов круга. Нужно создать для неё схемы секторов с указанными идентификаторами.</p><p>Если места с одним и тем же ID сектора в сервисе продажи билетов визуально разбиты на несколько отдельных групп мест (Зелёный театр, Воронеж) - нужно создать для этих разных групп мест отдельные схемы секторов с похожими идентификаторами (например, места с ID сектора <em>123</em> будут хранится в схемах секторов с идентификаторами <em>1231</em>, <em>1232</em> и <em>1233</em>.</p></li></ol> Сервис продажи билетов ID схемы зала Название схемы зала схемы залов Пересоздать кэш выбранных схем Схема зала Секторы 