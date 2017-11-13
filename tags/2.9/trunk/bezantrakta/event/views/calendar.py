import calendar as cal
import datetime

from django.contrib.humanize.templatetags.humanize import naturalday
from django.db.models import F
from django.shortcuts import render

from ..cache import get_or_set_cache as get_or_set_event_cache
from ..models import Event


def calendar(request, year, month, day):
    """Фильтр событий, проходящих в выбранную дату и вывод их афиш в позиции ``small_vertical``.

    В текущей версии Django ``1.11`` удобнее фильтровать дату по вхождению в диапазон "текущая дата-следующая дата".
    Прямое равенство с датами пока не работает.
    Поэтому для фильтрации событий определяется, какая дата будет следующей после текущей.
    Если это последний день месяца - следующим будет первое число следующего месяца.
    Если это последний день года - следующим будет 1 января следующего года.

    Args:
        year (str): Год (``YYYY``).
        month (str): Месяц (``MM``).
        day (str): День (``DD``).
    """
    year = int(year)
    month = int(month)
    day = int(day)

    # Текущая дата
    current_timezone = request.city_timezone
    calendar_date = datetime.datetime(
        year=year,
        month=month,
        day=day,
    )
    calendar_date_localized = current_timezone.localize(calendar_date)

    # Последние дни в каждом месяце
    month_max_day_mapping = {
        1:  31,
        # Високосный год кратен 4, но при этом ЛИБО не кратен 100, ЛИБО кратен 400
        2:  29 if cal.isleap(year) else 28,
        3:  31,
        4:  30,
        5:  31,
        6:  30,
        7:  31,
        8:  31,
        9:  30,
        10: 31,
        11: 30,
        12: 31,
    }
    # Последний ли это день в текущем месяце или году
    is_last_day_of_month = day == month_max_day_mapping[month]
    is_last_day_of_year = month == 12

    # Параметры следующей даты
    if is_last_day_of_month:
        next_year = year
        next_month = month + 1
        next_day = 1
        if is_last_day_of_year:
            next_year = year + 1
            next_month = 1
            next_day = 1
    else:
        next_year = year
        next_month = month
        next_day = day + 1

    # Следующая дата
    calendar_next_date = datetime.datetime(
        year=next_year,
        month=next_month,
        day=next_day,
    )
    calendar_next_date_localized = current_timezone.localize(calendar_next_date)
    # Диапазон для фильтрации по текущей дате
    range_filter = (calendar_date_localized, calendar_next_date_localized)

    # Получение событий в заданный день
    events_on_date = list(Event.objects.select_related(
        'event_venue',
        'domain'
    ).annotate(
        uuid=F('id'),
    ).values(
        'uuid',
    ).filter(
        is_group=False,
        is_published=True,
        datetime__range=range_filter,
        domain_id=request.domain_id
    ).order_by(
        'datetime',
        'title'
    ))

    if events_on_date:
        for event in events_on_date:
            # Получение информации о каждом размещённом событии из кэша
            event.update(get_or_set_event_cache(event['uuid'], 'event'))

    context = {
        'title': 'События на {naturalday}'.format(naturalday=naturalday(calendar_date_localized)),
        'calendar_date': calendar_date_localized,
        'calendar_next_date': calendar_next_date_localized,
        'events_on_date': events_on_date,
    }

    return render(request, 'event/calendar.html', context)
