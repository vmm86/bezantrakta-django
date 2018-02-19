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
event_id = 2292  # test 2199
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
# py_result = ts.discover_events()

# SECTORS
# py_result = ts.sectors(event_id=event_id)
# SECTORS
# py_result = ts.sector_seats(event_id=event_id, sector_id=sector_id)
# SEATS AND PRICES
# py_result = ts.seats_and_prices(event_id=event_id)
#
# SCHEME
# py_result = ts.scheme(event_id=event_id)

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
#     '5_1_26': {'ticket_uuid': uuid.UUID('c909a29e-9001-4382-8308-fb612bcc95c1'), 'sector_id': 5, 'row_id': 1, 'seat_id': 26, },
# }
# py_result = ts.order_create(event_id=event_id, order_uuid=order_uuid, customer=customer, tickets=tickets)

# ORDER_CANCEL
# order_uuid = uuid.UUID('04f54215-066c-4877-8c7c-083264b82564')
# order_id = 47616
# tickets = {
#     '509_16_9': {'ticket_uuid': uuid.UUID('45974da2-547e-4185-812e-4560e5586eec'),
#     'sector_id': 509, 'row_id': 16, 'seat_id': 9, },
# }
# py_result = ts.order_cancel(event_id=event_id, order_uuid=order_uuid, order_id=order_id, tickets=tickets)

# ORDER_APPROVE
# event_id = 151
# order_uuid = uuid.UUID('b004469f-1be6-42be-9c91-14301c0cca9e')
# payment_id = '3141333342280100'
# payment_datetime = datetime.now()
# tickets = {
#     '22_14_31': {'ticket_uuid': uuid.UUID('64127eb5-1487-4597-a603-45e94a7b27c0'),
#     'sector_id': 22, 'row_id': 14, 'seat_id': 31, },
#     '22_14_32': {'ticket_uuid': uuid.UUID('dd3d3f7c-abc2-49d0-9991-0655a8dce53b'),
#     'sector_id': 22, 'row_id': 14, 'seat_id': 32, },
# }

# for ticket in tickets:
#     ticket['event_id'] = event_id
#     print('    ticket: ', ticket)
#     print(ts.ticket_status(**ticket))

# py_result = ts.order_approve(
#     event_id=event_id,
#     order_uuid=order_uuid,
#     payment_id=payment_id,
#     payment_datetime=payment_datetime,
#     tickets=tickets
# )

# # LOG
# py_result = ts.log(
#     from_date='21.12.2017', from_time='11:30', to_date='21.12.2017', to_time='12:10',
#     event_id=event_id, sector_id=529, row_id=8, seat_id=23
# )

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=180)
except NameError:
    pass
