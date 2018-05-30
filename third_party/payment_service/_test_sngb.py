import uuid
from pprint import pprint

from payment_service_abc import payment_service_factory

SNGB_TEST = {
    'mode': 'test',
    'test_merchant_id': '2009',
    'test_terminal_alias': '2009-BEZANTRAKTA',
    'test_psk': '338b23a05f875f8eef4a0095cc2e964796449142',
    'test_token': '12bcaf02b8da1c442d3c0df04c7ca615068acde18aaf6affbeced0d2a15e8e3e',

    'commission': 1.8,
    'timeout': 15,
}

SNGB_PROD = {
    'mode': 'prod',
    'prod_merchant_id': '1568',
    'prod_terminal_alias': '1568-alias',
    'prod_psk': 'fae9fa2ddff2d3c231134f4a8ffa3ed768152e78',
    'prod_token': 'c17cd3d987bb332e9c7b1ee62fd6b8e16b4172eddbf8364c48caa0f239ecb668',

    'commission': 1.8,
    'timeout': 15,
}

slug = 'sngb'
# init = SNGB_TEST
init = SNGB_PROD
ps = payment_service_factory(slug, init)

event_id = 171  # test
event_uuid = '3828f7f7-4008-416f-80eb-5c5df790f4d8'

customer = {
    'name': 'Посторонним В', 'email': 'vmm@rterm.ru', 'phone': '+74732000111',
}

# order_uuid = uuid.uuid4()
# order_id = 10
# overall = ps.decimal_price(2.25)

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
payment_id = '7660590561781340'
py_result = ps.payment_status(payment_id=payment_id)

# PAYMENT_REFUND
# order_id = 16180
# payment_id = '6234585261980990'
# amount = ps.decimal_price('10.00')
# py_result = ps.payment_refund(order_id=order_id, payment_id=payment_id, amount=amount)

try:
    print(type(py_result))
    pprint(py_result, indent=4, width=160)
except NameError:
    pass
