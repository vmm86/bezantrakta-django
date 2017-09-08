ORDER_DELIVERY = {
    'self':    'получение в кассе',
    'courier': 'доставка курьером',
    'email':   'электронный билет',
}

ORDER_PAYMENT = {
    'cash':   'наличные',
    'online': 'онлайн-оплата',
}

ORDER_STATUS = {
    'ordered':   {'color': 'blue',   'description': 'создан'},
    'cancelled': {'color': 'red',    'description': 'отменён'},
    'approved':  {'color': 'green',  'description': 'успешно завершён'},
    'refunded':  {'color': 'violet', 'description': 'возвращён'},
}
