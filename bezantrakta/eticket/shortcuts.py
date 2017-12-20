import barcode
import os
import pyqrcode
import re
import textwrap

from cairosvg import svg2pdf
from io import BytesIO
from barcode.writer import ImageWriter
from base64 import b64encode
from PIL import Image

from django.conf import settings
from django.template.loader import get_template


def render_eticket(context, logger):
    """Генерация PDF-файла электронного билета.

    Args:
        context (dict): Информация, необходимая для генерации файла билета.

            Содержимое ``context``:

                'url' (str):               URL станицы события на сайте.
                'event_title' (str):       Название события.
                'event_venue_title' (str): Название зала.
                'event_date' (str):        Человекопонятная дата события.
                'event_time' (str):        Человекопонятное время события.
                'event_min_age' (int):     Ограничение по возрасту (по умолчанию - ``0``).
                'poster' (str):            Относительный путь к файлу афиши ``small_vertical`` внутри папки ``MEDIA``.

                'ticket_service_order' (int): Идентификатор заказа в сервисе продажи билетов.

                'ticket_id' (uuid.UUID): Идентификатор билета в БД.
                'bar_code' (str):        Штрих-код.
                'sector_title' (str):    Название сектора.
                'row_id' (int):          Идентификатор ряда.
                'seat_title' (str):      Название места.
                'price' (Decimal):       Цена билета.

        logger (logging.RootLogger): Файл для логирования процесса генерации PDF-билета.

    Returns:
        str: Полный путь к сгенерированному файлу билета.
    """
    titles_max_chars = 26
    sector_max_chars = 40

    # Обрезка слишком длинных строковых значений и разбиение по словам для умещения в строке
    context['event_title'] = textwrap.shorten(
        context['event_title'], width=titles_max_chars*4, placeholder='...'
    )
    context['event_title'] = textwrap.wrap(context['event_title'], titles_max_chars)

    context['event_venue_title'] = textwrap.shorten(
        context['event_venue_title'], width=titles_max_chars*2, placeholder='...'
    )
    context['event_venue_title'] = textwrap.wrap(context['event_venue_title'], titles_max_chars)

    context['sector_title'] = textwrap.shorten(
        context['sector_title'], width=sector_max_chars, placeholder='...'
    )

    context['event_min_age'] = (
        '{min_age}+'.format(min_age=context['event_min_age']) if
        context['event_min_age'] else
        '0+'
    )

    context['price'] = int(context['price']) if context['price'] % 1 == 0 else context['price']

    # Полный путь к файлу афиши `small vertical` на сервере
    context['poster_path'] = '{media_root}/{poster}'.format(
        media_root=settings.MEDIA_ROOT,
        poster=context['poster']
    )
    # Афиша в base64
    context['poster_base64'] = poster_to_base64(context['poster_path'])
    # QR-код в base64
    context['qr_code_base64'] = qr_code_to_base64(context['url'])
    # Горизонтальный штрих-код в base64
    context['bar_code_h_base64'] = bar_code_to_base64('code128', context['bar_code'], 500, 175)
    # Вертикальный штрих-код в base64
    context['bar_code_v_base64'] = bar_code_to_base64('code128', context['bar_code'], 588, 125)

    # Генерация и сохранение файла билета
    output_name = '{order_id}_{ticket_id}.pdf'.format(
        order_id=context['ticket_service_order'],
        ticket_id=context['ticket_id']
    )
    full_output_path = os.path.join(
        settings.BEZANTRAKTA_ETICKET_PATH,
        context['domain_slug'],
        output_name
    )
    # Создание дерева папок до файла со стандартными правами 755
    if not os.path.exists(full_output_path):
        os.makedirs(os.path.dirname(full_output_path), mode=0o755, exist_ok=True)

    template = get_template('eticket/eticket.svg')
    ticket = re.sub(r'\n', r'', template.render(context))  # Минификация кода
    svg2pdf(bytestring=str.encode(ticket), write_to=full_output_path)
    logger.info('\nЭлектронный билет {output_name} успешно сгенерирован'.format(output_name=output_name))

    return full_output_path


def poster_to_base64(poster_path):
    """Конвертация файла афиши в base64.

    Args:
        poster_path (str): Полный путь к файлу афиши на сервере.

    Returns:
        str: Афиша в base64.
    """
    name, dot, extension = poster_path.rpartition('.')
    with open(poster_path, 'rb') as p:
        poster_file_base64 = b64encode(p.read()).decode('ascii')
    return 'data:image/{ext};base64,{b64}'.format(ext=extension, b64=poster_file_base64)


def bar_code_to_base64(bar_code_type, bar_code, width, height):
    """Создание PNG-файла штрих-кода в памяти и его ковертация в base64.

    Args:
        bar_code_type (str): Тип штрих-кода.
        bar_code (str): Значение штрих-кода.

    Returns:
        str: Штрих-код в base64.
    """
    writer_options = {
        'module_width': 0.5,
        'module_height': 30.0,
        'quiet_zone': 0.0,
        'font_size': 12,
        'text_distance': 0.0,
        'background': 'white',
        'foreground': 'black',
        'write_text': False,
        'text': '',
    }

    # Генерация изображения штрих-кода в памяти
    bc = BytesIO()
    barcode.generate(bar_code_type, bar_code, writer=ImageWriter(), writer_options=writer_options, output=bc)

    # Изменение размеров полученного изображения до необходимых
    img = Image.open(bc)
    img = img.resize((width, height), Image.HAMMING)
    bc2 = BytesIO()
    img.save(bc2, format='PNG')

    bc_base64 = b64encode(bc2.getvalue()).decode('ascii')
    return 'data:image/png;base64,{b64}'.format(b64=bc_base64)


def qr_code_to_base64(url):
    """Создание PNG-файла QR-кода в памяти и его ковертация в base64.

    Args:
        url (TYPE): Description

    Returns:
        str: QR-код в base64.
    """
    qrcode = pyqrcode.create(url)

    qr = BytesIO()
    qrcode.png(qr, scale=10, module_color=(0, 0, 0, 255), background=(255, 255, 255, 255), quiet_zone=0)

    qr_base64 = b64encode(qr.getvalue()).decode('ascii')
    return 'data:image/png;base64,{b64}'.format(b64=qr_base64)
