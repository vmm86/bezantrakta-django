# Варианты заказа билетов (комбинация способа получения билетов и способа оплаты)
# Упорядочены в порядке предпочтения для показа на шаге 2 заказа билетов
ORDER_TYPE = ('self_online', 'email_online', 'self_cash', 'courier_cash',)

# Способы получения и оплаты билетов для каждого варианта заказа
ORDER_TYPE_MAPPING = {
    'self_online':  {'delivery': 'self',    'payment': 'online', },
    'email_online': {'delivery': 'email',   'payment': 'online', },
    'self_cash':    {'delivery': 'self',    'payment': 'cash', },
    'courier_cash': {'delivery': 'courier', 'payment': 'cash', },
}

# Подписи способов получения билетов
ORDER_DELIVERY_CAPTION = {
    'self':    'получение в кассе',
    'courier': 'доставка курьером',
    'email':   'электронный билет',
}

# Подписи способов оплаты
ORDER_PAYMENT_CAPTION = {
    'cash':   'наличные',
    'online': 'онлайн-оплата',
}

# Подписи разных вариантов вычисления общей суммы заказа
ORDER_OVERALL_CAPTION = {
    'overall_total':            'Общая сумма заказа',
    'overall_extra':            'Всего с учётом сервисного сбора',
    'overall_courier':          'Всего с учётом доставки курьером',
    'overall_courier_extra':    'Всего с учётом доставки курьером и сервисного сбора',
    'overall_commission':       'Всего с учётом комиссии платёжной системы',
    'overall_commission_extra': 'Всего с учётом комиссии платёжной системы и сервисного сбора',
}

# Подписи статусов заказа и их визуальное оформление
ORDER_STATUS_CAPTION = {
    'reserved':  {'color': 'black',  'description': 'предварительный резерв'},

    'ordered':   {'color': 'blue',   'description': 'создан'},
    'cancelled': {'color': 'red',    'description': 'отменён'},
    'approved':  {'color': 'green',  'description': 'успешно завершён'},
    'refunded':  {'color': 'violet', 'description': 'возвращён'},
}
