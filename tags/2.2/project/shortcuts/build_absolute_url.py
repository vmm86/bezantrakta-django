from django.conf import settings


def build_absolute_url(domain, path=None):
    """Конструктор абсолютного URL-адреса с указанеим опциональной относительной ссылки.

    Если относительная ссылка задана - получаем полную абсолютную ссылку "``протокол-домен-ссылка``".
    Если относительная ссылка НЕ задана - получаем абсолютную ссылку "``протокол-домен``" (**без слэша в конце!**), которую можно подставлять к любым относительным ссылкам **со слэшем в начале** (например, в шаблоне).

    Args:
        domain (str): Домен сайта (главный или с поддоменом).
        url_path (str): Относительный URL после домена.

    Returns:
        str: Требуемый абсолютный URL.
    """
    protocol = 'https://' if settings.BEZANTRAKTA_IS_SECURE else 'http://'
    domain = domain[:-1] if domain[-1] == '/' else domain

    if path is None:
        output_url = '{protocol}{domain}'.format(
            protocol=protocol,
            domain=domain
        )
    else:
        path = path if path[0] == '/' else '/' + path

        output_url = '{protocol}{domain}{path}'.format(
            protocol=protocol,
            domain=domain,
            path=path
        )

    return output_url
