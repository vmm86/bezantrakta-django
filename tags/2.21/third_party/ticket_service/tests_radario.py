from pprint import pprint

from ticket_service_abc import ticket_service_factory

RADARIO_VRN = {
    'api_id': '15',
    'api_key': 'testing000',
    'city_id': 14,  # Воронеж
    'company_id': 1671,  # Камерный театр
    'company_title': 'Воронежский Камерный театр',
}

slug = 'radario'
init = RADARIO_VRN
ts = ticket_service_factory(slug, init)

# RADARIO_VRN
place_id = 1224
scheme_id = 7528  # Камерный театр
# event_id = 52238  # Тест (сектор без мест)
event_id = 73811  # Тест (зал)
# event_id = 130324
group_id = 2127  # Игроки
price_group_id = 341031

# VERSION
# py_result = ts.version()

# PLACES
py_result = ts.places()
# SCHEME
# py_result = ts.scheme(scheme_id=scheme_id)
# DISCOVER_SCHEMES
# py_result = ts.discover_schemes()

# GROUPS
# py_result = ts.groups()
# DISCOVER_GROUPS
# py_result = ts.discover_groups()

# EVENTS
# py_result = ts.events()
# py_result = ts.events(group_id=group_id)
# DISCOVER_EVENTS
# py_result = ts.discover_events()

# EVENT
# py_result = ts.event(event_id=event_id)

# SECTORS
# py_result = ts.sectors(scheme_id=scheme_id)
# SEATS AND PRICES
# py_result = ts.seats_and_prices(event_id=event_id, scheme_id=scheme_id)
# PRICE_GROUPS
# py_result = ts.price_groups(event_id=event_id)

# RESERVE (ADD OR REMOVE)
# action = 'add'
# # action = 'remove'
# py_result = ts.reserve(
#     action=action,
#     event_id=event_id,
#     price_group_id=price_group_id,
#     seat_id=110
# )

# ORDER_CREATE
customer = {
    'name': 'TestClient', 'email': 'test@rterm.ru', 'phone': '84739876543',
}
tickets = [
    {'ticket_uuid': 'c1d1d880-c3c8-4d9b-ada6-325501af1cf8', 'price_group_id': price_group_id, 'seat_id': 110, },
    # {'ticket_uuid': 'c0b88fc5-5f6b-4fcd-a19c-4f88f53bdf2b', 'price_group_id': price_group_id, 'seat_id': 109, },
]
# py_result = ts.order_create(event_id=event_id, customer=customer, tickets=tickets)

# ORDER
order_id = 1880161
# py_result = ts.order(order_id=order_id)

# ORDER_CANCEL
# py_result = ts.order_cancel(order_id=order_id)

# ORDER_APPROVE
# py_result = ts.order_approve(order_id=order_id)

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=160)
except NameError:
    pass

TEST_EVENT_52238 = {
    'age': 0,
    'beginDate': '2017-07-31T08:19:00.000+00:00',
    'category': 'Театры, шоу',
    'cityId': 14,
    'cityName': 'Воронеж',
    'companyId': 1671,
    'companyTitle': 'Воронежский Камерный театр',
    'currency': 'RUB',
    'description': None,
    'discountPercent': None,
    'endDate': '2017-07-31T08:19:00.000+00:00',
    'eventProviderId': None,
    'eventProviderName': None,
    'gmtOffset': 3.0,
    'groupId': None,
    'id': 52238,
    'images': '',
    'maxPrice': 1.0,
    'maxTicketCountPerOrder': None,
    'minPrice': 0.0,
    'placeAddress': 'ул. Карла Маркса, д. 55А',
    'placeId': 1224,
    'placeSchemeId': None,
    'placeSchemeImage': None,
    'placeTitle': 'Воронежский Камерный театр',
    'salesStopped': True,
    'superTagId': 2,
    'ticketCount': 7,
    'title': 'ТЕСТ КАССЫ',
    'videoUrl': None,
},

TEST_EVENT_73811 = {
    'age': 16,
    'beginDate': '2017-07-31T16:00:00.000+00:00',
    'category': 'Театры, шоу',
    'cityId': 14,
    'cityName': 'Воронеж',
    'companyId': 1671,
    'companyTitle': 'Воронежский Камерный театр',
    'currency': 'RUB',
    'description': 'Жорди Гальсеран\nстресс-тест\nРежиссер - Георгий Цхвирава',
    'discountPercent': None,
    'endDate': '2017-07-31T16:00:00.000+00:00',
    'eventProviderId': None,
    'eventProviderName': None,
    'gmtOffset': 3.0,
    'groupId': None,
    'id': 73811,
    'images': '[{"cover":true,"id":"ba5bd591b2aa4e02b0002b562fa0c81d.jpg","width":3508,"height":2481}]',
    'maxPrice': 1200.0,
    'maxTicketCountPerOrder': None,
    'minPrice': 1.0,
    'placeAddress': 'ул. Карла Маркса, д. 55А',
    'placeId': 1224,
    'placeSchemeId': 7528,
    'placeSchemeImage': None,
    'placeTitle': 'Воронежский Камерный театр',
    'salesStopped': True,
    'superTagId': 2,
    'ticketCount': 34,
    'title': 'тест',
    'videoUrl': None,
}
