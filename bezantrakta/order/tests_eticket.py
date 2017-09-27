from decimal import Decimal
from io import BytesIO
from xhtml2pdf import pisa

from django.template.loader import get_template

from project.shortcuts import build_absolute_url


def render_to_pdf(template, context, output_file):
    template = get_template(template)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
    if not pdf.err:
        # return HttpResponse(result.getvalue(), content_type='application/pdf')
        # output = open(os.path.join(org_output, current_output_file), 'w')
        output = open(output_file, 'w')
        output.write(pdf)
        print('rendered')
    return None

context = {
    'url': build_absolute_url('nsk', '/afisha/2017/09/01/19-00/test-novosibirsk-1916/'),
    'title':        'Борис Годунов гастроли Воронежского Камерного театра',
    'event_date':   '32 декабря',
    'event_time':   '16:00',
    'event_year':   '2017',
    'venue_title':  'Воронежский Камерный театр',
    'min_age':      '12+',
    'poster':       '/media/nsk/event/2017-09-01_19-00_test-novosibirsk-1916/small_vertical.png',

    'order_id':     336951,
    'ticket_id':    'c1d1d880-c3c8-4d9b-ada6-325501af1cf8',  # ID билета
    'bar_code':     '00269695239039573856',
    'sector_title': 'ложа амфитеатра, правая сторона',
    'row_id':       6,
    'seat_id':      18,
    'price':        Decimal(1.0).quantize(Decimal('0.00')),
}

render_to_pdf('order/eticket.svg', context, 'xhtml2pdf_test.pdf')
