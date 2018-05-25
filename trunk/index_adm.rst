###########################
Справка для администраторов
###########################

.. epigraph::

  Хотели как лучше, а получилось как всегда.

  -- Виктор Черномырдин

Новая платформа для продажи билетов http://bezantrakta.ru/ создавалась для того, чтобы:

* преодолеть имеющие в предыдущей версии системы недостатки,
* предоставить новые возможности для продажи билетов на сайте.

Администратор, работая в админ-панели, может создать любое число сайтов, работающих в разных городах России, наполнить каждый сайт необходимым содержимым и опубликовать его, предоставив пользователям возможность заходить на страницы событий и заказывать на них билеты.

В меню сначала указаны необходимые действия, которые нужно совершать администратору для создания новых сайтов и включения продажи билетов на них, а затем по порядку описываются все разделы админ-панели.

.. toctree::
  :maxdepth: 1
  :caption: Пошаговые инструкции

  docs/workflow/01_create_new_website
  docs/workflow/websites_list
  docs/workflow/02_organize_ticket_selling
  docs/workflow/03_order_workflow

.. toctree::
  :maxdepth: 1
  :caption: Описание админ-панели

  bezantrakta/simsim/index
  bezantrakta/simsim/choose_domain_or_city
  bezantrakta/simsim/last_actions
  bezantrakta/location/index
  bezantrakta/article/index
  bezantrakta/menu/index
  bezantrakta/banner/index
  third_party/ticket_service/index
  third_party/payment_service/index
  bezantrakta/event/index
  bezantrakta/order/index

.. toctree::
  :maxdepth: 1
  :caption: Прошлое и будущее проекта

  changelog
  todo
