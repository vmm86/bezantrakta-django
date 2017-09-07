from django.shortcuts import render


def browserconfig(request):
    context = {
        'host': request.url_domain,
    }
    return render(request, 'seo/browserconfig.xml', context, content_type='application/xml')


def manifest(request):
    context = {
        'name': request.url_domain,
        'short_name': request.domain_slug,
    }
    return render(request, 'seo/manifest.json', context, content_type='application/json')


def robots_txt(request):
    context = {
        'crawl_delay': 4.5,
        'host': request.url_domain,
    }
    return render(request, 'seo/robots.txt', context, content_type='text/plain')


def yandex_manifest(request):
    context = {
        'host': request.url_domain,
    }
    return render(request, 'seo/yandex.manifest.json', context, content_type='application/json')
