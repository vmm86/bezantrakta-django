#################
Задания manage.py
#################

Задание выполняется в *cron* и в заданный промежуток времени (сейчас ``15`` минут) **проверяет заказы с незавершёнными онлайн-оплатами** - созданные ранее заказы с онлайн-оплатой, на момент проверки находящиеся в статусе "**создан**", т.е. по каким-то причинам ещё НЕ подтверждённые и НЕ отменённые.

.. attention:: При выполнении задания проверяются не все незавершённые на данный момент заказы, а только те, у которых разница во времени от создания оплаты до текущего момента больше, чем время сессии на оплату (указанное в параметре ``timeout`` в JSON-настройках СОО, по умолчанию ``15`` минут). Таким образом проверяются только те заказы, время на оплату у которых уже истекло.

У каждого из заказов, просматириваемых при конкретном запуске задания, проверяется статус его оналйн-оплаты, после чего заказ завершается тем или  иным образом (подтверждается или отменяется).

.. automodule:: third_party.payment_service.management.commands.ps_checkup
