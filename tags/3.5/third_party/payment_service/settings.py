from collections import OrderedDict


# Настройки по умолчанию при создании нового сервиса продажи билетов
PAYMENT_SERVICE_SETTINGS_DEFAULT = OrderedDict([
    (
        'init',
        OrderedDict([
            ('user',      ''),
            ('test_pswd', ''),
            ('prod_pswd', '')
        ])
    ),
    (
        'commission', 0
    ),
    (
        'timeout', 15
    ),
])
