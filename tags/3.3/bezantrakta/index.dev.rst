Пакет ``bezantrakta``
=====================

..  toctree::
    :maxdepth: 3
    :caption: География сайтов

    location/index
    location/admin/index
    location/models/index
    location/middleware

..  toctree::
    :maxdepth: 3
    :caption: HTML-страницы

    article/index
    article/models/index
    article/views/index

..  toctree::
    :maxdepth: 3
    :caption: Меню

    menu/index
    menu/models/index
    menu/context_processors

..  toctree::
    :maxdepth: 3
    :caption: Баннеры

    banner/index
    banner/models/index
    banner/context_processors

..  toctree::
    :maxdepth: 1
    :caption: События

    event/index
    event/cache/index
    event/models/index
    event/views/index
    event/context_processors
    event/middleware

..  toctree::
    :maxdepth: 3
    :caption: Заказы

    order/index
    order/models/index
    order/views/index
    order/cache/index

..  toctree::
    :maxdepth: 3
    :caption: Электронные билеты

    eticket/index

..  toctree::
    :maxdepth: 3
    :caption: SEO-дополнения

    seo/index
    seo/views/index

..  toctree::
    :maxdepth: 3
    :caption: Кастомизация админ-панели

    simsim/index
    simsim/context_processors

* приложение ``article`` - текстовые страницы в HTML-разметке.
    * модель ``Article`` - текстовые страницы в HTML-разметке.
* приложение ``banner`` - группы баннеров и баннеры.
    * модель ``BannerGroup`` - группа баннеров.
    * модель ``Banner`` - баннеры.
* приложение ``eticket`` - генерация электронных билетов, отправляемых на электронную почту покупателя.
* приложение ``event`` - события.
    * модель ``Event`` - события.
    * модель ``EventGroupBinder`` - *Many2Many*-связка событий в группах.
    * модель ``EventVenue`` - залы.
    * модель ``EventCategory`` - категории событий.
    * модель ``EventContainer`` - контейнеры для отображения событий.
    * модель ``EventContainerBinder`` - *Many2Many*-связка событий и контейнеров.
    * модель ``EventLink`` - внешние ссылки со страниц событий.
    * модель ``EventLinkBinder`` - *Many2Many*-связка событий и ссылок.
* приложение ``location`` - география сайтов.
    * модель ``City`` - города.
    * модель ``Domain`` - сайты на отдельных поддоменах ``bezantrakta.ru``.
* приложение ``menu`` - меню и пункты меню.
    * модель ``Menu`` - меню.
    * модель ``MenuItem`` - пункты меню.
* приложение ``order`` - заказы билетов.
* приложение ``seo`` - динамически генерируемые "статические" файлы (иконки, json, txt, xml), либо необходимые для роботов поисковых систем, либо генерируемые динамически, будучи едиными для всех сайтов, но с некоторой специфичной для разных сайтов информацией.
* приложение ``simsim`` - кастомная админ-панель (переопределение или добавление некоторых компонентов).
