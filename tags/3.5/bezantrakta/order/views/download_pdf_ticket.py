import os
from django.conf import settings
from django.http import HttpResponse, FileResponse


def download_pdf_ticket(request, domain_slug, order_id, ticket_uuid):
    # Название файла PDF-билета
    pdf_ticket = '{order_id}_{ticket_uuid}.pdf'.format(
        order_id=order_id,
        ticket_uuid=ticket_uuid
    )
    # Полный путь к файлу PDF-билета на сервере
    pdf_ticket_path = os.path.join(
        settings.BEZANTRAKTA_ETICKET_PATH,
        domain_slug,
        pdf_ticket
    )
    # Вывод содержимого файла PDF-билета
    pdf_file = FileResponse(open(pdf_ticket_path, 'rb'))

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{pdf_ticket}"'.format(pdf_ticket=pdf_ticket)
    return response
