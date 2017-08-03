# Сайты Безантракта на базе Django

Основа проекта - фреймворк `Django` (стабильная LTS-версия 1.11), работающий на `Python 3` (желательно 3.5) в отдельном виртуальном окружении. Список пакетов для установки содержится в `requirements.txt`.

## Структура проекта

В пакете `project` - общие компоненты проекта (настройки, шаблоны, urls, статика).

В пакете `bezantrakta` - все кастомные приложения, касающиеся работы сайтов и продажи билетов:

* `simsim` - кастомная админ-панель (переопределение некоторых компонентов и стилей)
* `location` - география сайтов
- `City` - города
- `Domain` - сайты на отдельных поддоменах bezantrakta.ru
* `article` - HTML-страницы
* `menu` - меню и пункты меню
- `Menu` - меню
- `MenuItem` - пункты меню
* `banner` - группы баннеров и баннеры
- `BannerGroup` - группа баннеров
- `Banner` - баннеры
* `event` - события
- `Event` - события
- `EventGroupBinder` - M2M-связка событий в группах
- `EventVenue` - залы
- `EventCategory` - категории событий
- `EventContainer` - контейнеры для отображения событий
- `EventContainerBinder` - M2M-связка событий и контейнеров
- `EventLink` - внешние ссылки со страниц событий
- `EventLinkBinder` - M2M-связка событий и ссылок

Все модели, данные которые д.б. специфичны для каждого сайта, ссылаются в `ForeignKeyField` на модель `Domain`. Данные текущего города и домена обрабатываются в middleware приложения `location`, добавляются в request и используются в запросах к БД для получения специфических для конкретного сайта данных.

## Разработка и production deployment

Тестовая разработка - с помощью встроенного локального мини-веб-сервера на порту `8000`. В частности, позволяет не собирать статику при любом её изменении - обслуживание статики происходит автоматически.

Production deployment - на базе `nginx` как проксирующего веб-сервера и `uwsgi` как универсального сервера приложений, взаимодействующего с модулем `wsgi` в пакете `project`.

## Этапы production deployment

* Установка ОС на виртуальной машине (`Debian 9`).

* Настройка ОС (уствновка русской локали).

```bash
sudo su || su
dpkg-reconfigure locales
```

* Установка необходимых системных пакетов - `Python 3`, `PHP` для `phpMyAdmin`, `MySQL` или `MariaDB`, `nginx`, `uWSGI`, `SVN`. Если `PHP` вытянет за собой `Apache`, его нужно будет затем удалить за ненадобностью.

```bash
sudo su || su
apt-get install g++ gcc build-essential automake autoconf
apt-get install python3 python3-pip python-virtualenv virtualenv python-pkg-resources python3-virtualenv python3-dev libpython3-dev python-imaging libjpeg-dev
apt-get install php php-mbstring php-mysqli zip unzip
apt-get install (mysql-server libmysqlclient-dev) || (mariadb-server libmariadbclient-dev)
apt-get install nginx
apt-get install uwsgi uwsgi-plugin-python3 uwsgi-plugin-php
apt-get install subversion
```

* Настрока сервера баз данных и создание базы данных.

```mysql
nano "/etc/mysql/mariadb.conf.d/50-server"
# [mysqld]
# init_connect='SET collation_connection = utf8_general_ci'
# init_connect='SET NAMES utf8'
# character-set-server=utf8
# collation-server=utf8_general_ci

mysql

CREATE USER 'belcanto'@'localhost' IDENTIFIED BY '************';
CREATE DATABASE belcanto_bezantrakta_django CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON belcanto_bezantrakta_django.* TO 'belcanto'@'localhost';
```

* Получение актуальной версии `SVN`-репозитория.

```bash
cd /var/www
mkdir bezantrakta-django
cd bezantrakta-django
mkdir media static log
svn export http://svn.rterm.ru/bezantrakta-django/tags/X.Y.Z current_stable_tag
```

* Создание и активация виртуального окружения `Python 3`, установка необходимых Python-пакетов, синхронизация с БД.

```bash
cd /opt
mkdir bezantrakta-django

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
project = /var/www/bezantrakta-django/current_stable_tag
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

* Создание виртуального хоста `nginx`, взаимодействующего с сокетом uWSGI-приложения.

```bash
touch /etc/nginx/sites-available/bezantrakta.conf
```

```nginx
server {
    listen 80;
    listen [::]:80;
    root /var/www/bezantrakta-django/current_stable_tag;
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

10. Создание виртуального хоста `nginx` для `phpMyAdmin`.

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

11. Указывать в `hosts` все адреса сайтов, работающих локально на этой виртуальной машине, не нужно, если это настроено на уровне DNS (рекомендуется).

12. Перезапуск nginx и uWSGI, проверка работоспособности виртуального хоста.

```bash
service nginx configtest
service nginx restart

service uwsgi restart
```

## Разработка и поддержка

После любого изменения py-файлов в проекте:

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

При добавлении новых строк `_('...')` для файлов локализации:

```bash
[ venv ] python manage.py makemessages
# Заполнение строк локализации в папках `locale/ru/LC_MESSAGES/django.po`
[ venv ] python manage.py compilemessages
```
