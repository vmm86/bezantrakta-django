��    #      4  /   L        (   	  $   2  -   W  1   �     �     �     �     �               :     P     g     z     �     �     �  *   �      �         *   A  2   l  5   �     �     �  *     %   :  /   `  -   �  4   �  :   �     .  )   N  )   x  �  �  W   �	  _   �	     P
     ]
  �  q
  *   3     ^     g     �  &   �     �     �     �  ?  �     >   ,   O   #   |      �      �   #   �   C  �      )#     ,#  %   =#     c#     w#     ~#  X  �#  *   �(     )     )     *)     @)     T)                       #          	                                      
                                                          !                        "    event_admin_activate_or_deactivate_items ticket_service_admin_batch_set_cache ticket_service_admin_is_payment_service_added ticket_service_admin_ticket_service_schemes_count ticket_service_help_text ticketservice ticketservice_domain ticketservice_id ticketservice_is_active ticketservice_payment_service ticketservice_schemes ticketservice_settings ticketservice_slug ticketservice_slug_help_text ticketservice_title ticketservices ticketserviceschemesector ticketserviceschemesector_if_sector_exists ticketserviceschemesector_scheme ticketserviceschemesector_sector ticketserviceschemesector_sector_help_text ticketserviceschemesector_ticket_service_sector_id ticketserviceschemesector_ticket_service_sector_title ticketserviceschemesectors ticketserviceschemevenuebinder ticketserviceschemevenuebinder_event_venue ticketserviceschemevenuebinder_scheme ticketserviceschemevenuebinder_scheme_help_text ticketserviceschemevenuebinder_ticket_service ticketserviceschemevenuebinder_ticket_service_scheme ticketserviceschemevenuebinder_ticket_service_scheme_title ticketserviceschemevenuebinders ticketservicevenuebinder_if_scheme_exists ticketservicevenuebinder_if_sectors_exist Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2017-10-25 08:16+0000
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3);
 Включить или отключить сервисы продажи билетов Пересоздать кэш выбранных сервисов продажи билетов Оплата Схем залов <ul><li>{ <strong>init</strong> } - параметры для подключения (зависят от конкретного сервиса продажи билетов):<ul><li><strong>СуперБилет</strong><ul><li>string <strong>host</strong> - URL для отправки запросов к API,</li><li>string <strong>user</strong> - имя пользователя API,</li><li>string <strong>pswd</strong> - пароль пользователя API,</li><li>string <strong>mode</strong> - режим работы API (agency - Агентство, theatre - Театр).</li></ul></li><li><strong>Радарио</strong><ul><li>number <strong>api_id</strong> - идентификатор доступа к API,</li><li>string <strong>api_key</strong> - ключ доступа к API,</li><li>number <strong>city_id</strong> - идентификатор города в БД Радарио, в котором находится организатор,</li><li>number <strong>company_id</strong> - идентификатор организатора в БД Радарио,</li><li>string <strong>company_title</strong> - название организатора в БД Радарио.</li></ul></li></ul></li><li>[ <strong>schemes</strong> ] - список number идентификаторов схем залов в сервисе продажи билетов:При импорте информации из сервиса продажи билетов:<ul><li>Если список НЕпустой - будут импортироваться только те залы, идентификаторы которых указаны в этом списке;</li><li>Если список пустой - будут импортироваться ВСЕ залы.</li></ul></li><li>{ <strong>order</strong> } - включение/выключение способов заказа билетов на сайте (true - включено, false - отключено):<ul><li>boolean <strong>self_cash</strong> - получение в кассе (оплата наличными),</li><li>boolean <strong>courier_cash</strong> - доставка курьером (оплата наличными),</li><li>boolean <strong>self_online</strong> - получение в кассе (онлайн-оплата),</li><li>boolean <strong>email_online</strong> - электронный билет на email (онлайн-оплата).</li></ul></li><li>{ <strong>order_description</strong> } - сопроводительный текст к способам заказа билетов на 2-м шаге заказа билетов (строка с HTML-кодом):<ul><li>string <strong>self_cash</strong> - получение в кассе (оплата наличными),</li><li>string <strong>courier_cash</strong> - доставка курьером (оплата наличными),</li><li>string <strong>self_online</strong> - получение в кассе (онлайн-оплата),</li><li>string <strong>email_online</strong> - электронный билет на email (онлайн-оплата).</li></ul></li><li>{ <strong>order_email</strong> } - электронная почта для отправки сообщений администратору и покупателю:<ul><li>string <strong>user</strong> - логин (например, zakaz@bezantrakta.ru),</li><li>string <strong>pswd</strong> - пароль.</li></ul></li><li>{ <strong>order_email_description</strong> } - сопроводительный текст к способам заказа билетов в email-сообщении покупателю (строка с HTML-кодом):<ul><li>string <strong>self_cash</strong> - получение в кассе (оплата наличными),</li><li>string <strong>courier_cash</strong> - доставка курьером (оплата наличными),</li><li>string <strong>self_online</strong> - получение в кассе (онлайн-оплата),</li><li>string <strong>email_online</strong> - электронный билет на email (онлайн-оплата).</li></ul></li><li>number <strong>max_seats_per_order</strong> - максимальное число билетов в заказе (по умолчанию - 7).</li><li>number <strong>courier_price</strong> - стоимость доставки курьером в рублях (если 0 - доставка бесплатная).</li><li>number <strong>heartbeat_timeout</strong> - время в секундах, по истечении которого вновь запрашивается список доступных к продаже мест на схеме зала (по умолчанию - 10).</li><li>number <strong>seat_timeout</strong> - время в минутах, по истечении которого автоматически снимается предварительный резерв мест на схеме зала (по умолчанию - 15).</li></ul> сервис продажи билетов Сайт Идентификатор Работает Сервис онлайн-оплаты Схемы залов Настройки в JSON Псевдоним <p>Псевдоним должен совпадать с атрибутом <strong>slug</strong> класса соответствующего билетного сервиса.</p><p><ul><li><strong>superbilet</strong> для СуперБилет,</li><li><strong>radario</strong> для Радарио.</li></ul></p> Название сервисы продажи билетов сектор в схеме зала Сектор Схема зала Сектор в схеме зала <p>Схемы секторов создаются аналогично схеме зала.<br>Общая схема зала для работы с секторами должна содержать ссылки для открытия схем секторов по клику в отдельном блоке под общей схемой зала. При клике на каком-либо секторе на общей схеме зала выбранный сектор становится видимым, а все остальны секторы скрываются. ID Название секторы в схеме зала схема зала Зал Схема зала <p>Схема зала в HTML, как правило, на основе таблиц. Возможно использование SVG в тех случаях, когда это необходимо.</p><p>У родительского элемента всей схемы зала (&lt;table&gt; или &lt;svg&gt;) указывается класс <strong>stagehall</strong>.</p><p>Специфическим элементам схемы зала указываются соответствующие классы:</p><ul><li><strong>stage</strong> - сцена,</li><li><strong>sector</strong> - название сектора или номер ряда,</li><li><strong>seat</strong> - кликабельное место, которое также содержит data-атрибуты места из схемы в сервисе продажи билетов:<ul><li><strong>data-sector-id</strong> - идентификатор сектора,</li><li><strong>data-row-id</strong> - идентификатор ряда,</li><li><strong>data-seat-id</strong> - идентификатор места.</li></ul></li></ul><p>Остальные data-атрибуты подгружаются к каждому доступному для заказа месту при обновлении схемы зала на 1-м шаге заказа билетов.</p> Сервис продажи билетов ID Название схемы залов Схема зала Секторы 