from project.shortcuts import base_template_context_processor

from .models import BannerGroup, BannerGroupItem


def banner_group_items(request):
    """Получение информации о баннерах и её добавление в контекст шаблона."""
    if base_template_context_processor(request):
        banner_group_values = BannerGroup.objects.values('id', 'slug', 'title')

        banner_group = {
            bg['slug']: bg['title']
            for bg
            in banner_group_values
        }

        banner_group_items = {}
        for bg in banner_group_values:
            banner_group_items[bg['slug']] = list(BannerGroupItem.objects.filter(
                banner_group_id=bg['id'],
                is_published=True,
                domain_id=request.domain_id,
            ).values('title', 'img', 'href', 'order'))

        return {
            'banner_group': banner_group,
            'banner_group_items': banner_group_items,
        }
    else:
        return {}
