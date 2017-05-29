from .models import BannerGroup, BannerGroupItem


def banner_group_items(request):
    """
    Context processor that adds `banner` information to template context.
    """
    banner_group = {
        banner_group['slug']: banner_group['title']
        for banner_group
        in BannerGroup.objects.values('slug', 'title')
    }

    banner_group_items = {}
    for slug, title in banner_group.items():
        banner_group_items[slug] = BannerGroupItem.objects.filter(
            banner_group__slug=slug,
            domain__slug=request.domain,
        ).values('title', 'img', 'href', 'is_published')

    return {
        'banner_group': banner_group,
        'banner_group_items': banner_group_items,
    }
