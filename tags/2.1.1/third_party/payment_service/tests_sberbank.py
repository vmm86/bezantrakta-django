from pprint import pprint

from payment_service_abc import payment_service_factory

SBERBANK_VRN = {
    'mode': 'test',
    'user': 'bezantrakta-api',
    'test_pswd': 'bezantrakta',
    'prod_pswd': '',

    'commission': 2.8,
    'commission_included': False,
    'timeout': 15,

    'success_url': 'http://adm.bezantrakta-dev.rterm.ru/ps/success/',
    'error_url': 'http://adm.bezantrakta-dev.rterm.ru/ps/error/',
}

SBERBANK_NSK = {
    'mode': 'test',
    'user': 'nsk.bezantrakta-api',
    'test_pswd': 'nsk.bezantrakta',
    'prod_pswd': '',

    'commission': 2.8,
    'commission_included': False,
    'timeout': 15,

    'success_url': 'http://adm.bezantrakta-dev.rterm.ru/ps/success/',
    'error_url': 'http://adm.bezantrakta-dev.rterm.ru/ps/error/',
}

slug = 'sberbank'
init = SBERBANK_NSK
ps = payment_service_factory(slug, init)

domain = {
    'slug': 'nsk', 'title': 'Новосибирск',
}

# event_id = 52238  # Тест (сектор без мест)
event_id = 73811  # Тест (зал)
# event_id = 130324

order_uuid = '0a74b7bc-5ea5-451e-97aa-3fe13051d440'
order_id = 4
total = ps.decimal_price(10.0)

customer = {
    'name': 'Test Client', 'email': 'test@rterm.ru', 'phone': '+74739876543',
}

# PAYMENT_CREATE
# py_result = ps.payment_create(
#     domain=domain,
#     event_id=event_id,
#     order_uuid=order_uuid,
#     order_id=order_id,
#     total=total,
#     customer=customer,
# )

# PAYMENT_STATUS
payment_id = '0c8e3cd2-1704-49e4-b051-d310cffd39bf'
py_result = ps.payment_status(payment_id=payment_id)

# PAYMENT_REFUND
# py_result = ps.payment_refund(payment_id=payment_id, total=total)

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=160)
except NameError:
    pass
