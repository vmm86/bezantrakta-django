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
event_id = 1916  # nsk test
sector_id = 509

# THEATRE_VRN_TEST
# scheme_id = 1
# place_id = 1
# group_id = 1
# event_id = 615
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
py_result = ts.discover_events()

# SECTORS
# py_result = ts.sectors(event_id=event_id)
# SEATS AND PRICES
# py_result = ts.seats_and_prices(event_id=event_id)

# SCHEME
# py_result = ts.scheme(event_id=event_id)

order_uuid = 'c126ea91-f896-49ef-bdee-f8ab8fb6146a'
# RESERVE (ADD OR REMOVE)
# # action = 'add'
# action = 'remove'
# py_result = ts.reserve(
#     action=action,
#     event_id=event_id,
#     sector_id=sector_id,
#     row_id=11,
#     seat_id=35,
#     order_uuid=order_uuid
# )

# TICKET_STATUS
# py_result = ts.ticket_status(
#     # from_date='18.07.2017', from_time='15:30', to_date='18.07.2017', to_time='15:40',
#     event_id=event_id, ticket_uuid='c1d1d880-c3c8-4d9b-ada6-325501af1cf8', sector_id=sector_id, row_id=1, seat_id=34
# )

# ORDER_CREATE
# customer = {
#     'name': 'TestClient', 'email': 'test@rterm.ru', 'phone': '89201234567',
#     'is_courier': True, 'address': 'Воронеж',
#     # 'is_courier': False, 'address': '',
# }
tickets = [
    {'ticket_uuid': 'f2449bd0-2cf4-4153-b37f-15eaf21c15d0', 'sector_id': 509, 'row_id': 2, 'seat_id': 14, },
    {'ticket_uuid': '424603cc-1871-4f41-9cf1-e11ad525ae2f', 'sector_id': 509, 'row_id': 2, 'seat_id': 15, },
]
# py_result = ts.order_create(event_id=event_id, order_uuid=order_uuid, customer=customer, tickets=tickets)

# ORDER_DELETE
order_id = 39351
# py_result = ts.order_delete(event_id=event_id, order_uuid=order_uuid, order_id=order_id, tickets=tickets)

# ORDER_PAYMENT
# payment_id = '2d529111-1da0-455a-be55-3456eaf97055'
# payment_datetime = datetime.now()
# py_result = ts.order_payment(
#     event_id=event_id,
#     order_uuid=order_uuid,
#     payment_id=payment_id,
#     payment_datetime=payment_datetime,  # 'payment_date': '18.07.2017', 'payment_time': '15:40',
#     tickets=tickets
# )

# # LOG
# py_result = ts.log(
#     from_date='24.08.2017', from_time='12:00', to_date='26.08.2017', to_time='12:00',
#     event_id=event_id, sector_id=sector_id, row_id=1, seat_id=42
# )

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=160)
except NameError:
    pass
