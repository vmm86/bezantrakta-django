import uuid
from pprint import pprint

from ticket_service_abc import ticket_service_factory

RADARIO_VRN = {
    'api_version': 1.1,
    'api_id': 15,
    'api_key': 'testing000',
    'city_id': 14,  # Воронеж
    'company_id': 1671,  # Камерный театр
    'company_title': 'Воронежский Камерный театр',
}

slug = 'radario'
init = RADARIO_VRN
ts = ticket_service_factory(slug, init)
print(ts)

# RADARIO_VRN
place_id = 1224

data = {
    # тест (билеты без мест)
    'test_no_hall': {
        'scheme_id': 0,
        'event_id': 52238,
        'group_id': None,
        'sector_id': 382752,
    },
    # тест (большой зал)
    'test_big_hall': {
        'scheme_id': 7528,
        'event_id': 73811,
        'group_id': None,
        'sector_id': 2702934,
    },
    # Трамвай "Желание" (с местами на сцене)
    'desire': {
        'scheme_id': 8440,
        'event_id': 238743,
        'group_id': 2124,
        'sector_id': 2701104,
    },
    # Гоголь переоделся Пушкиным (малый зал)
    'gogol': {
        'scheme_id': 14115,
        'event_id': 239722,
        'group_id': 4021,
        'sector_id': 2704603,
    },
    # Каренин (малый зал)
    'karenin': {
        'scheme_id': 14116,
        'event_id': 239720,
        'group_id': 3930,
        'sector_id': 2704602,
    },
}

test_data = data['test_no_hall']
# test_data = data['test_big_hall']
# test_data = data['desire']
# test_data = data['gogol']
# test_data = data['karenin']

# VERSION
# py_result = ts.version()

# PLACES
# py_result = ts.places()
# SCHEME
# py_result = ts.scheme(scheme_id=test_data['scheme_id'])
# py_result = ts.scheme(scheme_id=test_data['scheme_id'], raw=True)
# DISCOVER_SCHEMES
# py_result = ts.discover_schemes()

# GROUPS
# py_result = ts.groups()
# DISCOVER_GROUPS
# py_result = ts.discover_groups()

# EVENTS
# py_result = ts.events()
# py_result = ts.events(group_id=test_data['group_id'])
# DISCOVER_EVENTS
# py_result = ts.discover_events()

# EVENT
# py_result = ts.event(event_id=test_data['event_id'])
# py_result = ts.event(event_id=234266)

# SECTORS
# py_result = ts.sectors(event_id=test_data['event_id'])
# SEATS AND PRICES
# py_result = ts.seats_and_prices(event_id=test_data['event_id'])

# RESERVE (ADD OR REMOVE)
# action = 'add'
# # action = 'remove'
# py_result = ts.reserve(
#     action=action,
#     event_id=test_data['event_id'],
#     sector_id=test_data['sector_id'],
#     seat_id=110
# )

# ORDER_CREATE
# customer = {
#     'name': 'TestClient', 'email': 'test@rterm.ru', 'phone': '+74732000111',
# }
# tickets = {
#     '10': {
#         'ticket_uuid': uuid.uuid4(),
#         'sector_id': test_data['sector_id'], 'row_id': 0, 'seat_id': 10,
#     }
# }
# py_result = ts.order_create(event_id=test_data['event_id'], customer=customer, tickets=tickets)

# ORDER
# order_id = 2509480
# py_result = ts.order(order_id=order_id)

# ORDER_CANCEL
# order_id = 2508941
# py_result = ts.order_cancel(order_id=order_id)

# ORDER_APPROVE
# order_id = 2508952
# py_result = ts.order_approve(order_id=order_id)

# ORDER_REFUND
# order_id = 2508833
# reason = 'Посторонним В'
# py_result = ts.order_refund(order_id=order_id, reason=reason)

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
