import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import HttpResponse


class JsonResponseUTF8(HttpResponse):
    """Удобное создание JSON-ответа с выводом любого не-ASCII текста в UTF-8.

    Args:
        response (list|dict): Ответ для конвертации в JSON.
    """
    def __init__(self, response, status=None, **kwargs):
        # HTTP-код ответа (по умолчанию 200)
        kwargs['status'] = status or 200

        kwargs.setdefault('content_type', 'application/json')

        json_dumps_params = {'ensure_ascii': False, }
        response = json.dumps(response, cls=DjangoJSONEncoder, **json_dumps_params)

        super(JsonResponseUTF8, self).__init__(content=response, **kwargs)
