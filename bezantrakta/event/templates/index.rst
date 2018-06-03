#######
Шаблоны
#######

* ``posters_big`` - отображение афиш в больших контейнерах.

* ``posters_small_vertical`` - отображение афиш в контейнере "**маленькие вертикальные**" (как опубликованных "**на главной**", так и **при фильтрации событий**).

* ``events_on_index`` - вывод событий "на главной".

  * наследует ``index.html``,
  * включает ``posters_small_vertical.html``, ``share_help.html``.

* ``filter_calendar`` - фильтрация событий по дате в календаре.

  * наследует ``index.html``,
  * включает ``posters_small_vertical.html``.

* ``filter_search`` - фильтрация событий в текстовом поиске.

  * наследует ``index.html``,
  * включает ``posters_small_vertical.html``.

* ``filter_category`` - фильтрация событий по категории.

  * наследует ``index.html``,
  * включает ``posters_small_vertical.html``.

* ``filter_venue`` - фильтрация событий по залу.

  * наследует ``index.html``,
  * включает ``posters_small_vertical.html``.
