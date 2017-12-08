# Сайты Безантракта на базе Django

## Структура проекта

Содержимое модулей проекта документируется в *docstrings* и в построчных комментариях, а содержимое *docstings*, в свою очередь, используется при автоматизированном создании HTML-документации из исходных ``*.rst``-файлов, находящихся в дереве проекта и документирующих соответствующие модули.

Документация для разработчиков генерируется с помощью **Sphinx** выполнением команды ``make html`` в корне проекта. Сгенетированная документация для разработчиков находится в папке `docs`.

Документация для администраторов включена в страницы админ-панели.

## Разработка и *production deployment*

Тестовая разработка - либо с помощью встроенного локального мини-веб-сервера на порту `8000`, либо на локальном веб-сервере (настройки идентичны *production deployment*). Встроенный локальный мини-веб-сервер, в частности, настроен таким образом, что позволяет НЕ собирать статику при любом её изменении - обслуживание статики происходит автоматически.

*Production deployment* - на базе `nginx` как проксирующего веб-сервера и `uwsgi` как универсального сервера приложений, взаимодействующего с модулем `wsgi` в пакете `project`.

## Этапы *production deployment*

* Установка операционной системы (`Debian 9`) на виртуальной машине.

* Настройка ОС.

```bash
sudo su || su
# Установка русской локали
dpkg-reconfigure locales
# Установка часового пояса в `UTC`
dpkg-reconfigure tzdata
```

* Установка необходимых системных пакетов - `Python 3`, `PHP` для `phpMyAdmin`, `MySQL` или `MariaDB`, `nginx`, `uWSGI`, `SVN` или `Git`. Если `PHP` вытянет за собой `Apache`, его нужно будет затем удалить за ненадобностью.

```bash
sudo su || su
apt-get install g++ gcc build-essential automake autoconf gettext
apt-get install python3 python3-pip python-virtualenv virtualenv python-pkg-resources python3-virtualenv python3-dev libpython3-dev python-imaging libjpeg-dev python3-lxml python3-dev libffi-dev
apt-get install php php-mbstring php-mysqli zip unzip
# ИЛИ MySQL, ИЛИ MariaDB
apt-get install (mysql-server libmysqlclient-dev) || (mariadb-server libmariadbclient-dev)
apt-get install nginx
apt-get install uwsgi uwsgi-plugin-python3 uwsgi-plugin-php
# ИЛИ SVN, ИЛИ Git
apt-get install (subversion) || (git)
```

* Настройка сервера баз данных и создание БД (на примере `MariaDB`).

```mysql
nano "/etc/mysql/mariadb.conf.d/50-server"
```
```ini
[mysqld]
init_connect='SET collation_connection = utf8_general_ci'
init_connect='SET NAMES utf8'
character-set-server=utf8
collation-server=utf8_general_ci
```
```mysql
mysql

CREATE USER 'belcanto'@'localhost' IDENTIFIED BY '************';
CREATE DATABASE belcanto_bezantrakta_django CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON belcanto_bezantrakta_django.* TO 'belcanto'@'localhost';
```

* Получение актуальной версии репозитория (на примере `SVN`).

```bash
cd /var/www
mkdir bezantrakta-django
cd bezantrakta-django
mkdir media static log
svn export http://svn.rterm.ru/bezantrakta-django/tags/X.Y bezantrakta_latest
```

* Создание и активация виртуального окружения `Python 3`, установка необходимых Python-пакетов, синхронизация с БД.

```bash
cd /opt
mkdir bezantrakta-django

# В зависимости от реализации virtual environment
(virtualenv -p /usr/bin/python3 venv || pyvenv venv)
source venv/bin/activate

[ venv ] cd trunk
[ venv ] pip install -r requirements.txt
# Предварительно создать БД с именем, указанным в project.settings.base.DATABASES
[ venv ] python manage.py migrate
```

* Создание `uWSGI`-приложения.

```bash
touch /etc/uwsgi/sites-available/bezantrakta.ini
```
```ini
[uwsgi]
project = /var/www/bezantrakta-django/bezantrakta_latest
chdir = %(project)

plugin = python3
pythonpath = %(project)
virtualenv = /opt/bezantrakta-django/venv
module = project.wsgi:application

master = 1
workers = 4
cheaper = 1
idle = 8
vacuum = 1
```
```bash
ln -s /etc/uwsgi/apps-available/bezantrakta.ini /etc/uwsgi/apps-enabled/
```

* Создание виртуального хоста `nginx`, взаимодействующего с сокетом `uWSGI`-приложения.

```bash
touch /etc/nginx/sites-available/bezantrakta.conf
```
```nginx
server {
    listen 80;
    listen [::]:80;
    root /var/www/bezantrakta-django/bezantrakta_latest;
    server_name bezantrakta.ru *.bezantrakta.ru;

    client_body_buffer_size 10M;
    client_max_body_size    10M;

    access_log /var/log/nginx/bezantrakta.access.log;
    error_log /var/log/nginx/bezantrakta.error.log info;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/run/uwsgi/app/belcanto/socket;
    }

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
}
```
```bash
ln -s /etc/nginx/sites-available/bezantrakta.conf /etc/nginx/sites-enabled/
```

* Скачать, распаковать и настроить `phpMyAdmin`.

```bash
cd /var/www
wget https://files.phpmyadmin.net/phpMyAdmin/X.Y.Z/phpMyAdmin-X.Y.Z-all-languages.zip
unzip phpMyAdmin-X.Y.Z-all-languages.zip
rm phpMyAdmin-X.Y.Z-all-languages.zip
mv phpMyAdmin-X.Y.Z-all-languages pma
cd pma
mv config.sample.inc.php config.inc.php
# Настройка config.inc.php
```

* Создание `uWSGI`-приложения для `phpMyAdmin`.

```bash
touch /etc/uwsgi/sites-available/pma.ini
```
```ini
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
```
```bash
ln -s /etc/uwsgi/apps-available/pma.ini /etc/uwsgi/apps-enabled/
```

* Создание виртуального хоста `nginx` для `phpMyAdmin`.

```bash
touch /etc/nginx/sites-available/pma.conf
```
```nginx
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

    location ~* \.($media_extensions)$ {
        root /var/www/pma;
        access_log off;
        expires 7d;
    }

}
```
```bash
ln -s /etc/nginx/sites-available/pma.conf /etc/nginx/sites-enabled/
```

* Указывать в `hosts` все адреса сайтов, работающих локально на этой виртуальной машине, не нужно, если это настроено на уровне `DNS` (*рекомендуется*).

* Перезапуск nginx и `uWSGI`, проверка работоспособности виртуального хоста.

```bash
service nginx configtest
service nginx restart

service uwsgi restart
```

* Для подсветки кода в редакторе `CKEditor` нужно распаковать содержимое архива `ckeditor_plugins/codemirror_1.15.zip` из репозитория в виртуальное окружение в папку `lib/python3.X/site-packages/ckeditor/static/ckeditor/ckeditor/plugins`, иначе редактор не будет работать. Если подсветка не нужна - закомментировать параметр `extraPlugins`.

## Разработка и поддержка

После любого изменения `*.py`-файлов в проекте:

```bash
service uwsgi restart
```

После изменения любой модели:

```bash
[ venv ] python manage.py makemigrations
[ venv ] python manage.py migrate
```

После любого изменения статических файлов в папках `static`:

```bash
[ venv ] python manage.py collectstatic
```

При добавлении новых строк `_('some_translation')` для файлов локализации:

```bash
# Создание строк для локализации в файлах локализации в папках `locale/ru/LC_MESSAGES/django.po`
[ venv ] python manage.py makemessages
# Заполнение строк для локализации
# Генерация новых бинарных файлов локализации из текстовых исходников
[ venv ] python manage.py compilemessages
```
