from django import template
from django.db.models import F

from bezantrakta.location.models import Domain

register = template.Library()


@register.inclusion_tag('admin/choose_domain.html', takes_context=True)
def choose_domain(context):
    # Список всех сайтов, город которых либо в процессе подготовки, либо включён
    domains = Domain.objects.select_related(
        'city',
    ).all().annotate(
        state=F('city__state'),
        timezone=F('city__timezone'),
    ).values(
        'title',
        'slug',
        'is_published',
        'state',
        'timezone',
    )
    return {
        'domains': domains,
        'bezantrakta_admin_domain_slug': context['bezantrakta_admin_domain_slug'],
    }
