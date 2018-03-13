База данных
===========

База данных проекта спроектирована на базе **MySQL** или **MariaDB** (в зависимости от операционной системы на сервере).

Все модели, данные которых специфичны для каждого сайта, ссылаются в ``ForeignKeyField`` на модель ``bezantrakta.location.models.Domain``. Данные текущего города и домена обрабатываются в *middleware* приложения ``location``, добавляются в объект ``request`` и используются в запросах к БД для получения специфических для конкретного сайта данных.

.. image:: /docs_dev/_static/db/belcanto_bezantrakta_django.png

:download:`Проект БД в MySQL Workbench </docs_dev/_static/db/belcanto_bezantrakta_django.mwb>`.
