# Варианты заказа билетов (комбинация способа получения билетов и способа оплаты)
ORDER_TYPE = ('self_cash', 'courier_cash', 'self_online', 'email_online')

# Способы получения билетов
ORDER_DELIVERY = {
    'self':    'получение в кассе',
    'courier': 'доставка курьером',
    'email':   'электронный билет',
}

# Способы оплаты
ORDER_PAYMENT = {
    'cash':   'наличные',
    'online': 'онлайн-оплата',
}

# Статусы заказа
ORDER_STATUS = {
    'ordered':   {'color': 'blue',   'description': 'создан'},
    'cancelled': {'color': 'red',    'description': 'отменён'},
    'approved':  {'color': 'green',  'description': 'успешно завершён'},
    'refunded':  {'color': 'violet', 'description': 'возвращён'},
}
