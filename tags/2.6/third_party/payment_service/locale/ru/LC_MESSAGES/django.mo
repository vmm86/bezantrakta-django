��          |      �          %   !     G     a     p     �     �  &   �     �     �             �  0  [   &  �  �  &   N     u     �  2   �  �   �     �	     �	     �	  (   �	        	   
                                                payment_service_admin_batch_set_cache payment_service_help_text paymentservice paymentservice_id paymentservice_is_active paymentservice_is_production paymentservice_is_production_help_text paymentservice_settings paymentservice_slug paymentservice_title paymentservices Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2017-09-06 12:53+0000
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3);
 Пересоздать кэш выбранных сервисов онлайн-оплаты <ul><li>{ <strong>init</strong> } - параметры для подключения (зависят от конкретного сервиса онлайн-оплаты):<ul><li><strong>Сбербанк</strong><ul><li>string <strong>user</strong> - имя пользователя API,</li><li>string <strong>test_pswd</strong> - пароль для тестовой оплаты НЕнастоящими деньгами,</li><li>string <strong>prod_pswd</strong> - пароль для production-оплаты настоящими деньгами.</li></ul></li><li><strong>СНГБ</strong></li></ul></li><li>number <strong>commission</strong> - комиссия сервиса онлайн-оплаты (если комиссия равна 0 - она НЕ прибавляется к сумме заказа),</li><li>number <strong>timeout</strong> - время на оплату заказа в минутах (по умолчанию - 15 минут).</li></ul> сервис онлайн-оплаты Идентификатор Работает Оплата настоящими деньгами <ul><li>Если включено - оплата настоящими деньгами.</li><li>Если отключено - тестовая оплата НЕнастоящими деньгами.</li></ul> Настройки Псевдоним Название сервисы онлайн-оплаты 