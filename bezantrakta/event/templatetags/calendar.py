from datetime import date, datetime, timedelta

from django import template
# from bezantrakta.models import Event

register = template.Library()


def get_month_last_day(year, month):
    if (month == 12):
        year += 1
        month = 1
    else:
        month += 1
    return date(year, month, 1) - timedelta(1)


@register.inclusion_tag('event/calendar.html')
def calendar(year, month):
    year = int(year)
    month = int(month)

    # event_list = Event.objects.filter(
    #     start_date__year=year,
    #     start_date__month=month
    # )

    month_first_day = date(year, month, 1)
    month_last_day = get_month_last_day(year, month)
    calendar_first_day = month_first_day - timedelta(month_first_day.weekday())
    calendar_last_day = month_last_day + timedelta(7 - month_last_day.weekday())

    body = []
    week = []
    head = []

    i = 0
    day = calendar_first_day
    while day <= calendar_last_day:
        if i < 7:
            head.append(day)
        cal_day = {}
        cal_day['day'] = day
        cal_day['event'] = False
        # for event in event_list:
        #     if day >= event.start_date.date() and day <= event.end_date.date():
        #         cal_day['event'] = True
        if day.month == month:
            cal_day['in_month'] = True
        else:
            cal_day['in_month'] = False
        week.append(cal_day)
        if day.weekday() == 6:
            body.append(week)
            week = []
        i += 1
        day += timedelta(1)

    return {'body': body, 'head': head}


@register.filter('if_today')
def if_today(day):
    if day == datetime.today().date():
        return 'today'
    else:
        return ''
