from collections import OrderedDict


# Настройки по умолчанию при создании нового события
EVENT_SETTINGS_DEFAULT = OrderedDict([
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
        'extra',
        OrderedDict([
            ('self_cash',    0),
            ('courier_cash', 0),
            ('self_online',  0),
            ('email_online', 0)
        ])
    ),
])
