###############
SEO-оптимизация
###############

Динамически генерируемые "статические" файлы, необходимые для представления сайта в Интернете и SEO-оптимизации:

* ``browserconfig.xml``
* ``manifest.json``
* ``robots.txt``
* ``yandex.manifest.json``

Содержимое файлов генерируется динамически "на лету", по необходимости используя специфичную информацию конкретного сайта, открытого в данный момент.

.. only:: dev

  *************
  Представления
  *************

  Файл browserconfig.xml
  ======================
  .. automodule:: bezantrakta.seo.views.browserconfig

  Файл manifest.json
  ==================
  .. automodule:: bezantrakta.seo.views.manifest

  Файл robots.txt
  ===============
  .. automodule:: bezantrakta.seo.views.robots_txt

  Файл yandex.manifest.json
  =========================
  .. automodule:: bezantrakta.seo.views.yandex_manifest
