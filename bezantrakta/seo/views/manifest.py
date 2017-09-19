from django.shortcuts import render


def manifest(request):
    context = {
        'name': request.url_domain,
        'short_name': request.domain_slug,
    }
    return render(request, 'seo/manifest.json', context, content_type='application/json')
