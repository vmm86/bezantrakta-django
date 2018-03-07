from operator import itemgetter

from django import template
from django.db.models import F, Q

from bezantrakta.location.models import City, Domain

register = template.Library()


@register.inclusion_tag('admin/choose_domain.html', takes_context=True)
def choose_domain(context):
    """Список всех городов без сайтов и всех сайтов, статус города у которых "в процессе подготовки" или "включён"."""
    # Все сайты
    domains = list(Domain.objects.select_related(
        'city',
    ).all().annotate(
        domain_id=F('id'),
        domain_title=F('title'),
        domain_slug=F('slug'),
        domain_is_published=F('is_published'),

        city_id=F('city__id'),
        city_slug=F('city__slug'),
        city_state=F('city__state'),
        timezone=F('city__timezone'),
    ).values(
        'domain_id',
        'domain_title',
        'domain_slug',
        'domain_is_published',

        'city_id',
        'city_slug',
        'city_state',
        'timezone',
    ))

    # Города без привязанных к ним сайтов
    cities = list(City.objects.annotate(
        domain_title=F('title'),
        domain_slug=F('slug'),

        city_id=F('id'),
        city_slug=F('slug'),
        city_state=F('state'),
    ).filter(
        Q(
            Q(state=True) | Q(state=None),
            Q(domain__isnull=True)
        )
    ).values(
        'domain_title',
        'domain_slug',

        'city_id',
        'city_slug',
        'city_state',
        'timezone',
    ).distinct())

    if cities:
        for city in cities:
            city['domain_id'] = 0
            city['domain_is_published'] = False

        domains += cities

        domains = sorted(domains, key=itemgetter('domain_title'))

    return {
        'domains': domains,
        'bezantrakta_admin_domain_slug': context['bezantrakta_admin_domain_slug'],
    }
