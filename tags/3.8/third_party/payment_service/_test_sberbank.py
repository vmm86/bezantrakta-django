from pprint import pprint

from payment_service_abc import payment_service_factory

SBERBANK_VRN = {
    'mode': 'prod',
    'user': 'bezantrakta-api',
    'test_pswd': 'bezantrakta',
    'prod_pswd': 'zyUnW8Dp2LoL',

    'commission': 0,
    'timeout': 15,
}

SBERBANK_TAM = {
    'mode': 'prod',
    'user': 'tam-bezantrakta-api',
    'test_pswd': 'tam-bezantrakta',
    'prod_pswd': '3v8!8A<oIzVi',

    'commission': 0,
    'timeout': 15,
}

SBERBANK_VLUKI = {
    'mode': 'test',
    'user': 'vluki-api',
    'test_pswd': 'vluki',
    'prod_pswd': '',

    'commission': 0,
    'timeout': 15,
}

SBERBANK_NSK = {
    'mode': 'test',
    'user': 'nsk.bezantrakta-api',
    'test_pswd': 'nsk.bezantrakta',
    'prod_pswd': '',

    'commission': 0,
    'timeout': 15,
}

slug = 'sberbank'
init = SBERBANK_VRN
# init = SBERBANK_TAM
# init = SBERBANK_VLUKI
# init = SBERBANK_NSK
ps = payment_service_factory(slug, init)

# event_id = 52238  # Тест (сектор без мест)
event_id = 73811  # Тест (зал)
# event_id = 130324

# event_uuid = '407b7b8a-28a4-470b-b7b9-53753cae3550'

# customer = {
#     'name': 'Test Client', 'email': 'test@rterm.ru', 'phone': '+74739876543',
# }

# order_uuid = '0a74b7bc-5ea5-451e-97aa-3fe13051d440'
# order_id = 1
# overall = ps.decimal_price(10.0)

# PAYMENT_CREATE
# py_result = ps.payment_create(
#     event_uuid=event_uuid,
#     event_id=event_id,
#     order_uuid=order_uuid,
#     order_id=order_id,
#     customer=customer,
#     overall=overall,
# )

# PAYMENT_STATUS
# payment_id = None
payment_id = '7156761c-9dca-72e1-7156-761c00005ab5'
py_result = ps.payment_status(payment_id=payment_id)

# PAYMENT_REFUND
# payment_id = '7095edf4-5f3f-7e80-7095-edf400005ab5'
# amount = ps.decimal_price(1.03)
# py_result = ps.payment_refund(payment_id=payment_id, amount=amount)

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=160)
except NameError:
    pass
