data = {}
data['FIXED'] = {
    'order_created': {
        'order_id': 1234567,
        'tickets': [
            {'id': 5911927, 'tickettypeid': 2702934, 'seatnumber': 110, 'barcodekey': '110000000000'},
            {'id': 5911910, 'tickettypeid': 2702934, 'seatnumber': 57,  'barcodekey': '570000000000'},
            {'id': 5911906, 'tickettypeid': 2702934, 'seatnumber': 139, 'barcodekey': '139000000000'},
            {'id': 5911919, 'tickettypeid': 2702935, 'seatnumber': 138, 'barcodekey': '138000000000'},
            {'id': 5911917, 'tickettypeid': 2702935, 'seatnumber': 12,  'barcodekey': '120000000000'}
        ]
    },
    'kwargs': {
        'tickets': {
            '110': {'ticket_uuid': '89f51286-84f3-4522-ba2f-b2cbca38477b',
                    'ticket_id': '110', 'sector_id': 2702934, 'seat_id': 110, 'is_fixed': True},
            '57':  {'ticket_uuid': '8cfa1022-0660-4f88-838a-cb61f06d67b8',
                    'ticket_id': '57',  'sector_id': 2702934, 'seat_id': 57,  'is_fixed': True},
            '139': {'ticket_uuid': '3b311727-9897-4b1e-a776-a6c989e34bb5',
                    'ticket_id': '139', 'sector_id': 2702934, 'seat_id': 139, 'is_fixed': True},
            '138': {'ticket_uuid': '813ba770-71a8-45d0-9c08-5694383e013f',
                    'ticket_id': '138', 'sector_id': 2702934, 'seat_id': 138, 'is_fixed': True},
            '12':  {'ticket_uuid': 'f3149ee6-50d4-4c94-bd84-ef238a7615a8',
                    'ticket_id': '12',  'sector_id': 2702934, 'seat_id': 12,  'is_fixed': True}
        }
    }
}
data['NON_FIXED'] = {
    'order_created': {
        'order_id': 1234567,
        'tickets': [
            {'id': 5911915, 'tickettypeid': 382752, 'seatnumber': None, 'barcodekey': '100000000000'},
            {'id': 5911978, 'tickettypeid': 382752, 'seatnumber': None, 'barcodekey': '300000000000'},
            {'id': 5911970, 'tickettypeid': 382754, 'seatnumber': None, 'barcodekey': '200000000000'},
            {'id': 5911976, 'tickettypeid': 382754, 'seatnumber': None, 'barcodekey': '500000000000'},
            {'id': 5911918, 'tickettypeid': 382752, 'seatnumber': None, 'barcodekey': '400000000000'}
        ]
    },
    'kwargs': {
        'tickets': {
            '3':  {'ticket_uuid': '86fbc167-5f80-472d-843e-9cc9ac13cc65',
                   'ticket_id': '3',  'sector_id': 382752, 'seat_id': None, 'is_fixed': False},
            '5':  {'ticket_uuid': '937e55da-7db8-40d7-ac12-4ea081f850c5',
                   'ticket_id': '5',  'sector_id': 382752, 'seat_id': None, 'is_fixed': False},
            '12': {'ticket_uuid': 'ed9b50af-78b4-4ddc-8e9d-14ec61b32a36',
                   'ticket_id': '12', 'sector_id': 382752, 'seat_id': None, 'is_fixed': False},
            '16': {'ticket_uuid': 'e781fb26-e4f0-4aa4-b9c1-36d54153b2e7',
                   'ticket_id': '16', 'sector_id': 382752, 'seat_id': None, 'is_fixed': False},
            '20': {'ticket_uuid': '26d0231d-e0a2-4276-92be-9159615926c8',
                   'ticket_id': '20', 'sector_id': 382752, 'seat_id': None, 'is_fixed': False}
        }
    }
}
data['MIXED'] = {
    'order_created': {
        'order_id': 1234567,
        'tickets': [
            {'id': 5911927, 'tickettypeid': 2702934, 'seatnumber': 110,  'barcodekey': '110000000000'},
            {'id': 3000000, 'tickettypeid': 382754,  'seatnumber': None, 'barcodekey': '300000000000'},
            {'id': 5911906, 'tickettypeid': 2702934, 'seatnumber': 139,  'barcodekey': '139000000000'},
            {'id': 5911919, 'tickettypeid': 2702935, 'seatnumber': 138,  'barcodekey': '138000000000'},
            {'id': 5000000, 'tickettypeid': 382752,  'seatnumber': None, 'barcodekey': '500000000000'}
        ]
    },
    'kwargs': {
        'tickets': {
            '110': {'ticket_uuid': '89f51286-84f3-4522-ba2f-b2cbca38477b',
                    'ticket_id': '110', 'sector_id': 2702934, 'seat_id': 110, 'is_fixed': True},
            '16':  {'ticket_uuid': 'e781fb26-e4f0-4aa4-b9c1-36d54153b2e7',
                    'ticket_id': '16', 'sector_id': 382752,  'seat_id': None, 'is_fixed': False},
            '139': {'ticket_uuid': '3b311727-9897-4b1e-a776-a6c989e34bb5',
                    'ticket_id': '139', 'sector_id': 2702934, 'seat_id': 139, 'is_fixed': True},
            '138': {'ticket_uuid': '813ba770-71a8-45d0-9c08-5694383e013f',
                    'ticket_id': '138', 'sector_id': 2702934, 'seat_id': 138, 'is_fixed': True},
            '12':  {'ticket_uuid': 'ed9b50af-78b4-4ddc-8e9d-14ec61b32a36',
                    'ticket_id': '12', 'sector_id': 382752,  'seat_id': None, 'is_fixed': False},
        }
    }
}

response = {}
response['tickets'] = {}

# TEST = 'FIXED'
# TEST = 'NON_FIXED'
TEST = 'MIXED'

success_condition = 'success' not in data[TEST]['order_created'] or data[TEST]['order_created']['success']
if success_condition and 'order_id' in data[TEST]['order_created']:
    response['success'] = True
    response['order_id'] = data[TEST]['order_created']['order_id']

    created_fixed_tickets = [t for t in data[TEST]['order_created']['tickets'] if t['seatnumber']]
    created_non_fixed_tickets = [t for t in data[TEST]['order_created']['tickets'] if not t['seatnumber']]

    kwargs_fixed_tickets = [t for tid, t in data[TEST]['kwargs']['tickets'].items() if t['is_fixed']]
    kwargs_non_fixed_tickets = [t for tid, t in data[TEST]['kwargs']['tickets'].items() if not t['is_fixed']]

    added_tids = set()
    added_barcodes = set()

    if created_fixed_tickets:
        print('\nFIXED SEATS')
        # Билеты С фиксированной рассадкой
        for cft in created_fixed_tickets:
            for kft in kwargs_fixed_tickets:
                if cft['seatnumber'] == kft['seat_id']:
                    ticket_id = kft['ticket_id']
                    print('fixed seat: {}'.format(ticket_id))
                    if cft['barcodekey'] not in added_barcodes and ticket_id not in added_tids:
                        ticket = {}
                        ticket['ticket_uuid'] = kft['ticket_uuid']
                        ticket['bar_code'] = cft['barcodekey']
                        added_tids.add(ticket_id)
                        added_barcodes.add(ticket['bar_code'])
                        response['tickets'][ticket_id] = ticket.copy()
                        print('    fixed ticket: {}'.format(ticket))
                        print('        added_tids: {}'.format(added_tids))
                        print('        added_barcodes: {}'.format(added_barcodes))
                else:
                    continue

    if created_non_fixed_tickets:
        cnft_barcodes = [t['barcodekey'] for t in created_non_fixed_tickets]

        print('\nNON FIXED SEATS')
        # Билеты БЕЗ фиксированной рассадки
        for knft in kwargs_non_fixed_tickets:
            ticket_id = knft['ticket_id']
            print('non-fixed seat: {}'.format(ticket_id))

            ticket = {}
            ticket['ticket_uuid'] = knft['ticket_uuid']
            ticket['bar_code'] = cnft_barcodes.pop()
            response['tickets'][ticket_id] = ticket.copy()
            added_tids.add(ticket_id)
            added_barcodes.add(ticket['bar_code'])
            print('    non-fixed ticket: {}'.format(ticket))
            print('        added_tids: {}'.format(added_tids))
            print('        added_barcodes: {}'.format(added_barcodes))

else:
    print('\nreturn order_created:',)
    print(data[TEST]['order_created'])

print('\nreturn response:')
for tid, t in response['tickets'].items():
    print('    * {}: {}'.format(tid, t))
