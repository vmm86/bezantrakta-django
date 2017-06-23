from django import template
from django.db.models import Q

from bezantrakta.location.models import Domain

register = template.Library()


@register.inclusion_tag('admin/choose_domain.html', takes_context=True)
def choose_domain(context):
    # Список всех сайтов, город которых либо в процессе подготовки, либо включён
    domains = Domain.objects.filter(
        Q(city__state__isnull=True) | Q(city__state=True),
    ).values(
        'title',
        'slug',
        'is_published',
    )
    return {
        'domains': domains,
        'bezantrakta_domain_slug': context['bezantrakta_domain_slug'],
    }
