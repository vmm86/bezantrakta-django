MONTH_NAMES = {
    1:  'января',
    2:  'февраля',
    3:  'марта',
    4:  'апреля',
    5:  'мая',
    6:  'июня',
    7:  'июля',
    8:  'августа',
    9:  'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря',
}


def humanize_date(input_date):
    """Получение человекопонятной даты с русскоязычным месяцем в родительном падеже."""
    humanized_date = '{day} {genitive_month} {year} г.'.format(
        day=input_date.strftime('%-d'),
        genitive_month=MONTH_NAMES[int(input_date.strftime('%-m'))],
        year=input_date.strftime('%Y')
    )

    return humanized_date
