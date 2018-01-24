from collections import OrderedDict


# Настройки по умолчанию при создании нового сервиса продажи билетов
TICKET_SERVICE_SETTINGS_DEFAULT = OrderedDict([
    (
        'init',
        OrderedDict([
            ('host', 'http://sbgs.gastroli.net/cgi-bin/agency-belcanto/STicketGate.exe/wsdl/ISTicket'),
            ('user', 'sbgs2'),
            ('pswd', 'qwaz56ty'),
            ('mode', 'agency')
        ])
    ),
    (
        'schemes', []
    ),
    (
        'order',
        OrderedDict([
            ('self_cash',    True),
            ('courier_cash', True),
            ('self_online',  True),
            ('email_online', True)
        ])
    ),
    (
        'order_description',
        OrderedDict([
            ('self_cash',    ''),
            ('courier_cash', ''),
            ('self_online',  ''),
            ('email_online', '')
        ])
    ),
    (
        'order_email',
        OrderedDict([
            ('user', 'zakaz_new@bezantrakta.ru'),
            ('pswd', 'CNmkWDYRDEcP')
        ])
    ),
    (
        'order_email_description',
        OrderedDict([
            ('self_cash',    ''),
            ('courier_cash', ''),
            ('self_online',  ''),
            ('email_online', '')
        ])
    ),
    (
        'max_seats_per_order', 7
    ),
    (
        'courier_price', 0
    ),
    (
        'promoter', 'ООО «БЕЛЬКАНТО» ИНН 3662243480'
    ),
    (
        'seller', 'ИП Карюков Игорь Леонидович ИНН 366202613092 ОГРНИП 313366803500228'
    ),
])
