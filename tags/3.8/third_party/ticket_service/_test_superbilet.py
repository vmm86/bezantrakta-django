import uuid
from datetime import datetime
from pprint import pprint

from ticket_service_abc import ticket_service_factory

AGENCY_VRN = {
    'host': 'http://sbgs.gastroli.net/cgi-bin/agency-belcanto/STicketGate.exe/wsdl/ISTicket',
    'user': 'sbgs2',
    'pswd': 'qwaz56ty',
    'mode': 'agency',
}

THEATRE_VRN = {
    'host': 'http://sbgs.gastroli.net/cgi-bin/theatre-opera-ballet/STicketGate.exe/wsdl/ISTicket',
    'user': 'sbgs3',
    'pswd': 'badss53201',
    'mode': 'theatre',
}

THEATRE_VRN_TEST = {
    'host': 'http://sbgs.gastroli.net/cgi-bin/theatre-opera-ballet_test/STicketGate.exe/wsdl/ISTicket',
    'user': 'sbgs3',
    'pswd': 'badss53201',
    'mode': 'theatre',
}

AGENCY_SAR = {
    'host': 'http://sbgs.gastroli.net/cgi-bin/agency-radiobereg/STicketGate.exe/wsdl/ISTicket',
    'user': 'sbgs_sar',
    'pswd': 'SaR1bE6i3Z',
    'mode': 'agency',
}

AGENCY_SUR = {
    'host': 'http://sbgs.gastroli.net/cgi-bin/agency-belcanto-pojidaev/STicketGate.exe/wsdl/ISTicket',
    'user': 'sbgs_sur',
    'pswd': 'SuR2aD4i7e',
    'mode': 'agency',
}

AGENCY_NVAR = {
    'host': 'http://sbgs.gastroli.net/cgi-bin/agency-nvartovsk/STicketGate.exe/wsdl/ISTicket',
    'user': 'sbgs_nvar',
    'pswd': 'NVr3kE8i6Sk',
    'mode': 'agency',
}

slug = 'superbilet'
init = AGENCY_VRN
# init = THEATRE_VRN
# init = THEATRE_VRN_TEST
# init = AGENCY_SAR
# init = AGENCY_SUR
# init = AGENCY_NVAR
ts = ticket_service_factory(slug, init)
print(ts)

# AGENCY_VRN
place_id = 14
scheme_id = 20
group_id = 214
# event_id = 1875  # Test
# event_id = 1887  # Billy's Band
# event_id = 1913  # arh test
# event_id = 1914  # vluki test
# event_id = 1915  # vluki test
event_id = 2470  # test Цирк
# event_id = 116  # test Сургут
sector_id = 509

# THEATRE_VRN_TEST
# scheme_id = 1
# place_id = 1
# group_id = 1
# event_id = 725
# sector_id = 15

# VERSION
# py_result = ts.version()

# PLACES
# py_result = ts.places()
# SCHEMES
# py_result = ts.schemes(place_id=place_id)
# SCHEME
# py_result = ts.scheme(event_id=event_id)
# DISCOVER_SCHEMES
# py_result = ts.discover_schemes()

# GROUPS
# py_result = ts.groups()
# DISCOVER_GROUPS
# py_result = ts.discover_groups()

# EVENTS
# py_result = ts.events()
# py_result = ts.events(place_id=place_id)
# py_result = ts.events(scheme_id=scheme_id)
# DISCOVER_EVENTS
py_result = ts.discover_events()

# SECTORS
# py_result = ts.sectors(event_id=event_id)
# SECTORS
# py_result = ts.sector_seats(event_id=event_id, sector_id=sector_id)
# SEATS AND PRICES
# py_result = ts.seats_and_prices(event_id=event_id)

# order_uuid = uuid.UUID('987bdbb4-0180-4839-93b3-2bb2ff42729c')
# RESERVE (ADD OR REMOVE)
# action = 'add'
# # action = 'remove'
# py_result = ts.reserve(
#     action=action,
#     event_id=event_id,
#     sector_id=529,
#     row_id=8,
#     seat_id=23,
#     order_uuid=order_uuid
# )

# TICKET_STATUS
# py_result = ts.ticket_status(
#     # from_date='18.07.2017', from_time='15:30', to_date='18.07.2017', to_time='15:40',
#     event_id=event_id, ticket_uuid='c1d1d880-c3c8-4d9b-ada6-325501af1cf8', sector_id=529, row_id=8, seat_id=23
# )

# ORDER_CREATE
# customer = {
#     'name': 'TestClient', 'email': 'test@rterm.ru', 'phone': '+74732000111',
#     'is_courier': True, 'address': 'Воронеж',
#     # 'is_courier': False, 'address': '',
# }
# tickets = {
#     '5_1_26': {'ticket_uuid': uuid.UUID('c909a29e-9001-4382-8308-fb612bcc95c1'),
#                'sector_id': 5, 'row_id': 1, 'seat_id': 26, },
# }
# py_result = ts.order_create(event_id=event_id, order_uuid=order_uuid, customer=customer, tickets=tickets)

# ORDER_CANCEL
# event_id = 185
# order_uuid = uuid.UUID('fdc4b427-0561-4247-8ce2-e19caffbffb4')
# order_id = 16442
# tickets = {
#     '24_1_15': {'ticket_uuid': uuid.UUID('53b2d4ec-71e0-403b-9152-11942197435d'),
#                 'sector_id': 24, 'row_id': 1, 'seat_id': 15},
#     '24_1_16': {'ticket_uuid': uuid.UUID('147e62d3-3bb4-4a17-bf39-153df8f2843e'),
#                 'sector_id': 24, 'row_id': 1, 'seat_id': 16},
# }
# py_result = ts.order_cancel(event_id=event_id, order_uuid=order_uuid, order_id=order_id, tickets=tickets)

# ORDER_APPROVE
# event_id = 151
# order_uuid = uuid.UUID('b004469f-1be6-42be-9c91-14301c0cca9e')
# payment_id = '3141333342280100'
# payment_datetime = datetime.now()
# tickets = {
#     '22_14_31': {'ticket_uuid': uuid.UUID('64127eb5-1487-4597-a603-45e94a7b27c0'),
#                  'sector_id': 22, 'row_id': 14, 'seat_id': 31, },
#     '22_14_32': {'ticket_uuid': uuid.UUID('dd3d3f7c-abc2-49d0-9991-0655a8dce53b'),
#                  'sector_id': 22, 'row_id': 14, 'seat_id': 32, },
# }

# ORDER_REFUND
# order_id = 47963
# order_uuid = uuid.UUID('b004469f-1be6-42be-9c91-14301c0cca9e')
# payment_id = '3141333342280100'
# payment_datetime = datetime.now()
# reason = 'Посторонним В'
# py_result = ts.order_refund(order_id=order_id, reason=reason)

# py_result = ts.order_approve(
#     event_id=event_id,
#     order_uuid=order_uuid,
#     payment_id=payment_id,
#     payment_datetime=payment_datetime,
#     tickets=tickets
# )

# # LOG
# py_result = ts.log(
#     from_date='27.02.2018', from_time='09:00', to_date='27.02.2018', to_time='23:00',
#     event_id=event_id, sector_id=529, row_id=8, seat_id=23
# )

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=180)
except NameError:
    pass
