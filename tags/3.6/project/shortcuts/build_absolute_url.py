from django.conf import settings


def build_absolute_url(domain_slug, path=None):
    """Конструктор абсолютного URL-адреса с указанием опциональной относительной ссылки.

    Если относительная ссылка задана - получаем полную абсолютную ссылку *"протокол-домен-ссылка"*.
    Если относительная ссылка НЕ задана - получаем абсолютную ссылку *"протокол-домен"* (**без слэша в конце!**).
    Её можно подставлять к любым относительным ссылкам *со слэшем в начале* (например, в шаблоне).

    Args:
        domain_slug (str): Псевдоним (поддомен) текущего сайта.
        path (str): Опциональный относительный URL, добавляемый после домена.

    Returns:
        str: Требуемый абсолютный URL.
    """
    protocol = 'https://' if settings.BEZANTRAKTA_IS_SECURE else 'http://'

    domain = (
        '{domain}.{root}'.format(domain=domain_slug, root=settings.BEZANTRAKTA_ROOT_DOMAIN) if
        domain_slug != settings.BEZANTRAKTA_ROOT_DOMAIN_SLUG else
        '{root}'.format(root=settings.BEZANTRAKTA_ROOT_DOMAIN)
    )

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
