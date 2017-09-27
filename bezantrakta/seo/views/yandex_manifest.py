from django.shortcuts import render

from project.shortcuts import build_absolute_url


def yandex_manifest(request):
    context = {
        'logo_url': build_absolute_url(request.domain_slug, '/static/global/ico/yandex-tableau.png')
    }
    return render(request, 'seo/yandex.manifest.json', context, content_type='application/json')
