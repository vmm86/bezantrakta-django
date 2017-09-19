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
- `EventVenue` - залы
- `EventCategory` - категории событий
- `EventContainer` - контейнеры для отображения событий
- `EventContainerBinder` - M2M-связка событий и контейнеров
- `EventGroup` - группы из нескольких событий
- `EventGroupBinder` - M2M-связка событий и групп
- `EventLink` - внешние ссылки со страниц событий
- `EventLinkBinder` - M2M-связка событий и ссылок

Все модели, данные которые д.б. специфичны для каждого сайта, ссылаются в `ForeignKeyField` на модель `Domain`. Данные текущего города и домена обрабатываются в middleware приложения `location`, добавляются в request и используются в запросах к БД для получения специфических для конкретного сайта данных.

## Разработка и production deployment

Тестовая разработка - с помощью встроенного локального мини-веб-сервера на порту `8000`.

Production deployment - на базе `nginx` как проксирующего веб-сервера и `uwsgi` как универсального сервера приложений, взаимодействующего с модулем `wsgi` в пакете `project`.

## Этапы production deployment

1. Установка ОС на виртуальной машине (Debian 9).

2. Настройка ОС.

3. Установка необходимых системных пакетов - Python 3, PHP для phpMyAdmin, MySQL или MariaDB, nginx, uWSGI, SVN.

```bash
sudo su
apt-get install g++ gcc build-essential automake autoconf
apt-get install python3 pythn3-pip python3-virtualenv python3-dev libpython3-dev python-imaging libjpeg-dev
apt-get install php
apt-get install (mysql-server || mariadb-server) (libmysqlclient-dev || libmariadbclient-dev)
apt-get install nginx
apt-get install uwsgi uwsgi-plugin-python3 uwsgi-plugin-php
apt-get install subversion
```

4. Получение актуальной версии SVN-репозитория.

```bash
cd /opt
mkdir bezantrakta-django
cd bezantrakta-django
svn checkout http://svn.rterm.ru/bezantrakta-django
```

5. Создание symlink из `trunk` SVN-репозитория в папку `/var/www/`.

```bash
ln -s "/opt/bezantrakta-django/trunk" "/var/www/bezantrakta-django"
```

6. Создание и активация виртуального окружения Python 3, установка необходимых Python-пакетов, синхронизация с БД.

```bash
cd /opt/bezantrakta-django

(virtualenv -p /usr/bin/python3 venv || pyvenv venv)
source venv/bin/activate

[ venv ] cd trunk
[ venv ] pip install -r requirements.txt
# Предварительно создать БД с именем, указанным в project.settings.base.DATABASES
[ venv ] python manage.py migrate
```

7. Создание uWSGI-приложения.

```bash
touch /etc/uwsgi/sites-available/bezantrakta.ini
```

```ini
[uwsgi]
project = /var/www/bezantrakta-django/tags/1.0
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
ln -s /etc/uwsgi/sites-available/bezantrakta.ini /etc/uwsgi/sites-enabled/
```

8. Создание виртуального хоста nginx, взаимодействующего с сокетом uWSGI-приложения.

```bash
touch /etc/nginx/sites-available/bezantrakta.conf
```

```nginx
server {
    listen 80;
    listen [::]:80;
    root /var/www/bezantrakta-django/tags/1.0;
    server_name bezantrakta.rterm.ru *.bezantrakta.rterm.ru;

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

9. Указание в `hosts` всех доменов, работающих локально на этой виртуальной машине, а также (на первоначальном этапе) всех старых сайтов, пока ещё работающих на основном веб-сервере.

```bash
127.0.0.1    kur.bezantrakta.ru
127.0.0.1    lip.bezantrakta.run
...
5.9.222.194    bezantrakta.ru
5.9.222.194    theatre.bezantrakta.ru
...
```

10. Перезапуск nginx и uWSGI, проверка работоспособности виртуального хоста.

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
