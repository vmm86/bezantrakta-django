################################
Сайты Безантракта на базе Django
################################

********************
Документация проекта
********************
Исходные \*.rst-файлы документации распределены по дереву папок самого проекта. Сама HTML-документация генерируется с помощью `Sphinx <http://www.sphinx-doc.org/>`_ и сохраняется в папке ``docs``:

* справка для администраторов по работе админ-панели - в папке ``docs/adm``;
* документация для разработчиков - в папке ``docs/dev``.

Содержимое модулей проекта документируется в *docstrings* и в построчных комментариях, а содержимое *docstings*, в свою очередь, используется при автоматизированном создании HTML-документации из исходных \*.rst-файлов, находящихся в дереве проекта и документирующих соответствующие модули.

Сама сегнерированная HTML-документация *не хранится в системе контроля версий*. Поэтому генерировать документацию необходимо как при развёртывании проекта, так и после любых изменений в исходных \*.rst-файлах документации. Для этого нужно зайти в консоли в соответствующую папку (``docs/adm`` или ``docs/dev``) и выполнить в ней команду:

.. code-block:: bash

  make html

********************
Разные рабочие среды
********************
Тестовая разработка, промежуточная среда, *production deployment*.

В зависимости от рабочей среды за основу берётся тот или иной файл настроек по умолчанию в пакете ``project.settings``. Его нужно скопировать на 3 уровня выше пакета настроек, перименовать в ``settings.py`` и по необходимости отредактировать.

Для каждой новой мажорной версии проекта *желательно создавать заново* копию базы данных из предыдущей версии (например, ``belcanto_bezantrakta_django_3``) и новое виртуальное окружение (например, ``venv_v3``).

Название самой папки с текущей версией проекта (например, ``bezantrakta_latest``) при этом *должно оставаться неизменным*, т.к. в *cron* время от времени выполняются задания с указанием полного пути к файлам внутри проекта.

1. Тестовый **development**-проект для разработки на основе :download:`settings_01_development.py </project/settings/settings_01_development.py>`. Разработка проходит либо с помощью встроенного в Django мини-веб-сервера на порту ``8000``, либо на локальном веб-сервере (настройки и процесс развёртывания идентичны **production**, но с использованием настроек для дебаггинга). Встроенный локальный мини-веб-сервер настроен таким образом, что позволяет НЕ собирать статику при любом её изменении - обслуживание статики происходит автоматически.

2. Промежуточный **staging**-проект (*опционально*) на основе :download:`settings_02_staging.py </project/settings/settings_02_staging.py>`. Проект разворачивается на локальном веб-сервере (настройки и процесс развёртывания идентичны **production**) и может использоваться как промежуточная среда для предварительного тестирования обновлений проекта.

3. **Production**-проект на основе :download:`settings_03_production.py </project/settings/settings_03_production.py>`. Проект работает на базе ``nginx`` как проксирующего веб-сервера и ``uWSGI`` как универсального сервера приложений, взаимодействующего с модулем ``wsgi`` в пакете ``project``.

*******************
Тестовая разработка
*******************
После любого изменения ``*.py``-файлов в проекте:

.. code-block:: bash

  service uwsgi restart

После изменения любой модели:

.. code-block:: bash

  [ venv ] python manage.py makemigrations
  [ venv ] python manage.py migrate

После любого изменения статических файлов в папках ``static``:

.. code-block:: bash

  [ venv ] python manage.py collectstatic

При добавлении новых строк ``_('some_translation')`` для файлов локализации:

.. code-block:: bash

  # Создание строк для локализации в файлах локализации в папках ``locale/ru/LC_MESSAGES/django.po``
  [ venv ] python manage.py makemessages
  # Заполнение строк для локализации
  # Генерация новых бинарных файлов локализации из текстовых исходников
  [ venv ] python manage.py compilemessages

*********************
Production deployment
*********************

Первоначальное развёртывание проекта
====================================

* Установка операционной системы (``Debian 9``) на виртуальной машине.

* Настройка ОС.

.. code-block:: bash

  sudo su || su
  # Установка русской локали
  dpkg-reconfigure locales
  # Установка часового пояса в ``UTC``
  dpkg-reconfigure tzdata

* Установка необходимых системных пакетов - ``Python 3``, ``PHP`` для ``phpMyAdmin``, ``MySQL`` или ``MariaDB``, ``nginx``, ``uWSGI``, ``SVN`` или ``Git``. Если ``PHP`` вытянет за собой ``Apache``, его нужно будет затем удалить за ненадобностью.

.. code-block:: bash

  sudo su || su
  apt-get install g++ gcc build-essential automake autoconf gettext
  apt-get install python3 python3-pip python-virtualenv virtualenv python-pkg-resources python3-virtualenv python3-dev libpython3-dev python-imaging libjpeg-dev python3-lxml python3-dev libffi-dev
  apt-get install php php-mbstring php-mysqli zip unzip
  # ИЛИ MySQL, ИЛИ MariaDB
  apt-get install (mysql-server libmysqlclient-dev) || (mariadb-server libmariadbclient-dev)
  apt-get install nginx
  apt-get install uwsgi uwsgi-plugin-python3 uwsgi-plugin-php
  # SVN
  apt-get install subversion

* Настройка сервера баз данных и создание БД (на примере ``MariaDB``).

.. code-block:: mysql

  nano "/etc/mysql/mariadb.conf.d/50-server"

.. code-block:: ini

  [mysqld]
  init_connect='SET collation_connection = utf8_general_ci'
  init_connect='SET NAMES utf8'
  character-set-server=utf8
  collation-server=utf8_general_ci

.. code-block:: mysql

  mysql

  CREATE USER 'belcanto'@'localhost' IDENTIFIED BY '************';
  CREATE DATABASE belcanto_bezantrakta_django CHARACTER SET utf8 COLLATE utf8_general_ci;
  GRANT ALL PRIVILEGES ON belcanto_bezantrakta_django.* TO 'belcanto'@'localhost';

* Получение актуальной версии проекта из ``SVN``-репозитория.

.. code-block:: bash

  cd /var/www
  mkdir bezantrakta-django
  cd bezantrakta-django
  mkdir media static log
  svn export http://svn.rterm.ru/bezantrakta-django/tags/X.Y bezantrakta_latest

* Создание и активация виртуального окружения ``Python 3``, установка необходимых Python-пакетов, синхронизация с БД.

.. code-block:: bash

  cd /opt
  mkdir bezantrakta-django

  # В зависимости от реализации virtual environment
  (virtualenv -p /usr/bin/python3 venv || pyvenv venv)
  source venv/bin/activate

  [ venv ] cd trunk
  [ venv ] pip install -r requirements.txt
  # Предварительно создать БД с именем, указанным в project.settings.base.DATABASES
  [ venv ] python manage.py migrate

* Создание ``uWSGI``-приложения.

.. code-block:: bash

  touch /etc/uwsgi/sites-available/bezantrakta-django.ini

.. code-block:: ini
  :caption: bezantrakta-django.ini
  :name: bezantrakta-django.ini

  [uwsgi]
  project = /var/www/bezantrakta-django/bezantrakta_latest
  chdir = %(project)

  plugin = python3
  pythonpath = %(project)
  virtualenv = /opt/bezantrakta-django/venv
  module = project.wsgi:application

  master = true
  workers = 64

  harakiri = 60
  harakiri-verbose = true

  cheaper-algo = spare
  cheaper = 8
  cheaper-initial = 8
  cheaper-step = 4
  cheaper-idle = 60
  cheaper-overload = 30

  vacuum = true

.. code-block:: bash

  # Создать 2 символьные ссылки на основное uWSGI-приложение
  ln -s /etc/uwsgi/apps-available/bezantrakta-django.ini /etc/uwsgi/apps-available/bezantrakta-django_default.ini
  ln -s /etc/uwsgi/apps-available/bezantrakta-django.ini /etc/uwsgi/apps-available/bezantrakta-django_api.ini

  ln -s /etc/uwsgi/apps-available/bezantrakta-django_default.ini /etc/uwsgi/apps-enabled/
  ln -s /etc/uwsgi/apps-available/bezantrakta-django_api.ini /etc/uwsgi/apps-enabled/

* Создание виртуального хоста ``nginx``, взаимодействующего с сокетом ``uWSGI``-приложения.

.. code-block:: bash

  touch /etc/nginx/sites-available/bezantrakta-django.conf

.. code-block:: nginx
  :caption: bezantrakta-django.conf
  :name: bezantrakta-django.conf

  upstream bezantrakta-django_default {
      server unix:/run/uwsgi/app/bezantrakta-django_default/socket;
  }

  upstream bezantrakta-django_api {
      server unix:/run/uwsgi/app/bezantrakta-django_api/socket;
  }

  server {
      listen 80;
      listen [::]:80;
      root /var/www/bezantrakta-django/bezantrakta_latest;
      server_name bezantrakta.ru *.bezantrakta.ru;

      client_body_buffer_size 10M;
      client_max_body_size    10M;

      access_log /var/log/nginx/bezantrakta-django.access.log;
      error_log  /var/log/nginx/bezantrakta-django.error.log info;

      location /static/ {
          alias /var/www/bezantrakta-django/static/;
          access_log off;
          expires 3600;
      }

      location /media/ {
          alias /var/www/bezantrakta-django/media/;
          access_log off;
          expires 3600;
      }

      location /api/ {
          uwsgi_pass bezantrakta-django_api;
          include uwsgi_params;
          uwsgi_ignore_client_abort on;
      }

      location / {
          uwsgi_pass bezantrakta-django_default;
          include uwsgi_params;
          uwsgi_ignore_client_abort on;
      }
  }

  server {
      listen 80;
      listen [::]:80;
      server_name www.bezantrakta.ru;
      return 301 http://bezantrakta.ru$request_uri;
  }
  #server {
  #    listen 80;
  #    listen [::]:80;
  #    server_name ~^www\.(?<subdomain>\w+)\.bezantrakta.ru$;
  #    return 301 http://$subdomain.bezantrakta.ru$request_uri;
  #}

.. code-block:: bash

  ln -s /etc/nginx/sites-available/bezantrakta-django.conf /etc/nginx/sites-enabled/

* Скачать, распаковать и настроить ``phpMyAdmin``.

.. code-block:: bash

  cd /var/www
  wget https://files.phpmyadmin.net/phpMyAdmin/X.Y.Z/phpMyAdmin-X.Y.Z-all-languages.zip
  unzip phpMyAdmin-X.Y.Z-all-languages.zip
  rm phpMyAdmin-X.Y.Z-all-languages.zip
  mv phpMyAdmin-X.Y.Z-all-languages pma
  cd pma
  mv config.sample.inc.php config.inc.php
  # Настройка config.inc.php

* Создание ``uWSGI``-приложения для ``phpMyAdmin``.

.. code-block:: bash

  touch /etc/uwsgi/sites-available/pma.ini

.. code-block:: ini
  :caption: pma.ini
  :name: pma.ini

  [uwsgi]
  project = /var/www/pma
  chdir   = %(project)

  plugin      = php
  php-docroot = %(project)
  php-set     = date.timezone=Europe/Moscow
  php-set     = log_errors=1

  master  = true
  workers = 8
  cheaper = 2
  idle    = 30
  vacuum  = 1
  buffer-size = 65535

.. code-block:: bash

  ln -s /etc/uwsgi/apps-available/pma.ini /etc/uwsgi/apps-enabled/

* Создание виртуального хоста ``nginx`` для ``phpMyAdmin``.

.. code-block:: bash

  touch /etc/nginx/sites-available/pma.conf

.. code-block:: nginx
  :caption: pma.conf
  :name: pma.conf

  server {
      listen 80;
      listen [::]:80;
      server_name pma.bezantrakta.ru;
      root        /var/www/pma;
      access_log  /var/www/pma/log/access.log;
      error_log   /var/www/pma/log/error.log;

      location / {
          index index.php;
          try_files $uri $uri/ /index.php?q=$uri&$args;
      }

      location ~ \.php {
          include uwsgi_params;
          uwsgi_modifier1 14;
          uwsgi_pass unix:/run/uwsgi/app/pma/socket;
      }

      location ~\* \.($media_extensions)$ {
          root /var/www/pma;
          access_log off;
          expires 7d;
      }
  }

.. code-block:: bash

  ln -s /etc/nginx/sites-available/pma.conf /etc/nginx/sites-enabled/

.. important:: Рекомендуется НЕ указывать в ``hosts`` все адреса сайтов, работающих локально на этой виртуальной машине, и использовать вместо этого настройки на уровне **DNS**, чтобы у администраторов админ-панели сайта была возможность самостоятельно создать новый сайт в каком-то городе, наполнить его содержимым и опубликовать.

* Перезапуск ``nginx`` и ``uWSGI``, проверка работоспособности проекта.

.. code-block:: bash

  service nginx configtest
  service nginx restart

  service uwsgi restart

.. attention:: Для подсветки кода в редакторе ``CKEditor`` нужно распаковать содержимое архива ``ckeditor_plugins/codemirror_1.15.zip`` из репозитория в виртуальное окружение в папку ``lib/python3.X/site-packages/ckeditor/static/ckeditor/ckeditor/plugins``, иначе редактор не будет работать. Если подсветка не нужна - закомментировать параметр ``extraPlugins``.

Обновление ранее развёрнутого проекта
=====================================

Под ``X.Y`` понимается текущая новая версия проекта для обновления.

* Получение актуальной версии проекта из ``SVN``-репозитория.

.. code-block:: bash

  cd /var/www/bezantrakta-django
  svn export http://svn.rterm.ru/bezantrakta-django/tags/X.Y X.Y
  chown -R www-data:www-data X.Y

* Замена папки проекта со старой на новую, перезапуск ``nginx`` и ``uWSGI``.

.. code-block:: bash

  mv bezantrakta_latest bezantrakta_old && mv X.Y bezantrakta_latest && service nginx restart && service uwsgi restart

* Проверка работоспособности проекта. В случае успеха старую версию проекта в ``bezantrakta_old`` можно удалить.

.. code-block:: bash

  rm -rf bezantrakta_old
