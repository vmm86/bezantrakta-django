from django import template
from django.db.models import F

from bezantrakta.location.models import Domain

register = template.Library()


@register.inclusion_tag('admin/choose_domain.html', takes_context=True)
def choose_domain(context):
    """Список всех сайтов, статус города у которых либо "в процессе подготовки", либо "включён"."""
    domains = Domain.objects.select_related(
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
    )
    return {
        'domains': domains,
        'bezantrakta_admin_domain_slug': context['bezantrakta_admin_domain_slug'],
    }
