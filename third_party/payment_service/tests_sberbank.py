from pprint import pprint

from payment_service_abc import payment_service_factory

SBERBANK_VRN = {
    'mode': 'test',
    'user': 'bezantrakta-api',
    'test_pswd': 'bezantrakta',
    'prod_pswd': '',

    'commission': 2.8,
    'timeout': 15,
}

SBERBANK_VLUKI = {
    'mode': 'test',
    'user': 'vluki-api',
    'test_pswd': 'vluki',
    'prod_pswd': '',

    'commission': 2.8,
    'timeout': 15,
}

SBERBANK_NSK = {
    'mode': 'test',
    'user': 'nsk.bezantrakta-api',
    'test_pswd': 'nsk.bezantrakta',
    'prod_pswd': '',

    'commission': 2.8,
    'timeout': 15,
}

slug = 'sberbank'
init = SBERBANK_VLUKI
ps = payment_service_factory(slug, init)

# event_id = 52238  # Тест (сектор без мест)
event_id = 73811  # Тест (зал)
# event_id = 130324

event_uuid = '407b7b8a-28a4-470b-b7b9-53753cae3550'

customer = {
    'name': 'Test Client', 'email': 'test@rterm.ru', 'phone': '+74739876543',
}

order = {}
order['order_uuid'] = '0a74b7bc-5ea5-451e-97aa-3fe13051d440'
order['order_id'] = 1
order['total'] = ps.decimal_price(10.0)

# PAYMENT_CREATE
py_result = ps.payment_create(
    event_uuid=event_uuid,
    customer=customer,
    order=order,
)

# PAYMENT_STATUS
# payment_id = '0c8e3cd2-1704-49e4-b051-d310cffd39bf'
# py_result = ps.payment_status(payment_id=payment_id)

# PAYMENT_REFUND
# py_result = ps.payment_refund(payment_id=payment_id, total=total)

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=160)
except NameError:
    pass
