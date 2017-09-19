from django.shortcuts import render


def yandex_manifest(request):
    context = {
        'host': request.url_domain,
    }
    return render(request, 'seo/yandex.manifest.json', context, content_type='application/json')
