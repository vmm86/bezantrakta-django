��    `        �         (     )     /  +   K  &   w     �     �     �     �     �     �     	     )	     ;	     L	     ^	     p	     	     �	     �	     �	     �	     �	     �	     
     
     %
     4
     A
     P
  
   i
  
   t
     
     �
     �
     �
     �
     �
     �
       #   %     I     d      {     �     �     �     �     �     
     #     ?  "   S      v  $   �  "   �     �     �               2  $   M  #   r     �      �     �  $   �          &     6     G     ^     {      �     �  	   �     �     �     �               $     :     U     j     �     �  
   �     �     �  
   �     �     �               .  �  :  "   0  Q   S  Q   �  B   �     :     Q     i  �   �     D     M  O   `  >   �  E   �     5     <     K     X     e     r     �     �  �   �     �  +   �  ,   �     �  
          �  )     �'     �'  *   �'  %   !(     G(     ^(  2   o(  !   �(  !   �(     �(  �   )     �)     �)  �   �)     �*     �*  2   �*      +     3+     K+     c+     x+  +   �+  '   �+  /   �+  +   ,     D,     S,     f,  O   w,     �,     �,     �,  
   -  
   -     -  I  &-  O   p4     �4  /   �4     5     5  -   !5  �  O5  /   �6  -   (7     V7  (   e7     �7     �7  @   �7     �7     8     8     +8     :8  @   I8  /   �8     �8  "   �8     �8  
   �8     �8     9     "9     69            9   >   Y   3   $         _       E   )   F   T   R               ;       L   1   %       C   -   
   2      J   ]                 A                  .   6          W   S      	       B              [       =   4       I   5      ,              O   7   D   N             `       K   Q          X         !       ^                    M   +   #   G       /   '       H          U          Z      P   V   \       8   0          :                        (   &       @   <   ?      *   "    event event_admin_batch_set_cache event_admin_delete_non_ticket_service_items event_admin_publish_or_unpublish_items event_container_count event_datetime event_description event_description_help_text event_domain event_event_category event_event_container event_event_group event_event_link event_event_venue event_group_count event_is_group event_is_group_event event_is_group_group event_is_on_index event_is_published event_keywords event_keywords_help_text event_link_count event_min_age event_min_price event_promoter event_seller event_settings event_settings_help_text event_slug event_text event_ticket_service event_ticket_service_event event_ticket_service_scheme event_title event_title_help_text eventcategories eventcategory eventcategory_description eventcategory_description_help_text eventcategory_is_published eventcategory_keywords eventcategory_keywords_help_text eventcategory_slug eventcategory_title eventcategory_title_help_text eventcontainer eventcontainer_img_height eventcontainer_img_width eventcontainer_is_published eventcontainer_mode eventcontainer_mode_big_horizontal eventcontainer_mode_big_vertical eventcontainer_mode_small_horizontal eventcontainer_mode_small_vertical eventcontainer_order eventcontainer_slug eventcontainer_title eventcontainerbinder eventcontainerbinder_event eventcontainerbinder_event_container eventcontainerbinder_event_datetime eventcontainerbinder_img eventcontainerbinder_img_preview eventcontainerbinder_order eventcontainerbinder_order_help_text eventcontainerbinders eventcontainers eventgroupbinder eventgroupbinder_event eventgroupbinder_event_group eventgroupbinder_title eventgroupbinder_title_help_text eventgroupbinders eventlink eventlink_img eventlink_img_help_text eventlink_slug eventlink_title eventlinkbunder eventlinkbunder_event eventlinkbunder_event_link eventlinkbunder_href eventlinkbunder_img_preview eventlinkbunder_order eventlinkbunders eventlinks eventlinks_img_preview events eventvenue eventvenue_city eventvenue_slug eventvenue_title eventvenue_ts_schemes_count eventvenues Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2018-01-15 09:20+0000
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3);
 событие или группа Пересоздать кэш выбранных событий или групп Удалить группы/события, добавленные вручную Опубликовать или снять с публикации Контейнеров Дата события Метатег `description` Содержит ключевые слова или фразы, описывающие событие, но не более 3-5 шт.<br>Всего не более 150-200 символов. Сайт Категория Контейнеры, в которых отображается событие Группа, содержащая другие события Внешние ссылки, добавленные к событию Зал событий Группа Группа Группа На главной Публикация Метатег `keywords` Несколько ключевых слов или фраз, разделённых запятыми, которые описывают событие.<br>Всего не более 100-150 символов. Ссылок Возрастное ограничение Минимальная цена билета Организатор Агент Настройки в JSON <ul><li><strong>order</strong> { словарь 'ключ': 'значение' } - включение/выключение способов заказа билетов в событии (<em>true</em> - включено, <em>false</em> - отключено, по умолчанию - <em>true</em>):<ul><li><strong>self_cash</strong> логическое значение - получение в кассе (оффлайн-оплата),</li><li><strong>courier_cash</strong> логическое значение - доставка курьером (оффлайн-оплата),</li><li><strong>self_online</strong> логическое значение - получение в кассе (онлайн-оплата),</li><li><strong>email_online</strong> логическое значение - электронный билет на email (онлайн-оплата).</li></ul><ul></ul>Если какой-то вариант <strong>включен</strong> в настройках сервиса продажи билетов и <strong>отключен</strong> в событии - он НЕ отображается на шаге 2 заказа билетов для этого события.<br>Если какой-то вариант <strong>отключен</strong> в настройках сервиса продажи билетов и <strong>включен</strong> в событии - он в любом случае НЕ будет отображаться на шаге 2 заказа билетов для любого события в этом сервисе продажи билетов.</li><li><strong>extra</strong> { словарь 'ключ': 'значение' } - сервисный сбор в процентах от цены любого билета в событии (по умолчанию - <em>0</em>):<ul><li><strong>self_cash</strong> число - получение в кассе (оффлайн-оплата),</li><li><strong>courier_cash</strong> число - доставка курьером (оффлайн-оплата),</li><li><strong>self_online</strong> число - получение в кассе (онлайн-оплата),</li><li><strong>email_online</strong> число - электронный билет на email (онлайн-оплата).</li></ul>Если сервисный сбор равен <em>0</em> - он НЕ используется.</li><li><strong>title</strong> строка - произвольный текст поверх афиши (например, подпись события в группе или название города в конкретном событии, если он отличается от города сайта в целом).</li><li><strong>cancelled</strong> логическое значение - текст "Отменено" поверх афиши, если <strong style="color: red;">событие отменено</strong>.</li><li><strong>rescheduled</strong> логическое значение - текст "Перенесено" поверх афиши, если <strong style="color: blue;">событие перенесено</strong>.</li><li><strong>redirect</strong> строка - относительный адрес страницы события, на которую нужно перенаправлять пользователей, заходящих на страницу этого события, если это событие было перенесено (например, <em>/afisha/2018/05/16/19-00/shou-improvizatsiya-158/</em>). Перенаправление требуется, как правило, <strong>в случае переноса мероприятия</strong>.</li><li><strong>test</strong> логическое значение - афиши тестовых событий (имеющих этот параметр со значением true) в любом случае не показываются на сайте (только в тестовой версии). На страницы тестовых событий можно заходить напрямую из админ-панели, нажимая на кнопку "Смотреть на сайте".</li></ul> Псевдоним Описание события Сервис продажи билетов ID события или группы ID схемы зала Название Всего не более 60-65 символов. категории событий категория событий Метатег `description` Содержит ключевые слова или фразы, описывающие категорию, но не более 3-5 шт.<br>Всего не более 150-200 символов. Публикация Метатег `keywords` Несколько ключевых слов или фраз, разделённых запятыми, которые описывают категорию.<br>Всего не более 100-150 символов. Псевдоним Название Всего не более 60-65 символов. контейнер Высота афиши Ширина афиши Публикация Тип контейнера Большие горизонтальные Большие вертикальные Маленькие горизонтальные Маленькие вертикальные Порядок Псевдоним Название привязка афиш группы/события к контейнерам Событие Контейнер Дата события Афиша Афиша Порядок <div class="help"><p><strong>Маленькие вертикальные афиши нужно в любом случае добавлять для всех опубликованных групп и событий, не принадлежащих группам!</strong><br>Эти афиши используются для вывода событий при их фильтрации на сайте (по дате в календаре, категории, залу, в текстовом поиске), а также для генерации электронных PDF-билетов. <br>При отсутствии афиши будет выводиться картинка-заглушка с логотипом Безантракта <img src="/static/global/ico/favicon.ico" width="16" height="16">.</p><p>Афиша события ведёт на страницу этого события.</p><p><strong>Афиша группы ведёт на самое раннее на данный момент актуальное событие, принадлежащее этой группе</strong>. Если на данный момент все события в группе уже прошли, а новые ещё не созданы, афиша группы в любом случае НЕ выводится на сайте. Поэтому <strong>группы можно постоянно оставлять опубликованными</strong> (особенно, если в них периодически создаются похожие повторяющиеся события).</p><p>Если порядковые номера для показа афиш в одном контейнере одинаковые (например, <em>1</em>) – афиши сортируются по дате/времени события.</p></div> привязка афиш группы/события к контейнерам контейнеры привязка событий к группе Событие Группа Подпись события в группе <ul><li>Если событие в группе имеет особый статус, например, отдельные секторы зала в одном событии (танцпол, фанзона и т.п.). - указывается необходимое название.</li><li>Если это просто отдельные события в группе - поле остаётся пустым.</li></ul> привязка событий к группе внешняя ссылка в событии Логотип Размер логотипа 192x64 px. Псевдоним Название привязка внешних ссылок к событиям Событие Ссылка Внешняя ссылка Логотип Порядок привязка внешних ссылок к событиям внешние ссылки в событиях Логотип события или группы зал Город Псевдоним Название Схем залов залы 