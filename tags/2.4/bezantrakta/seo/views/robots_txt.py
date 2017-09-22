from django.shortcuts import render


def robots_txt(request):
    context = {
        'crawl_delay': 4.5,
        'host': request.url_domain,
    }
    return render(request, 'seo/robots.txt', context, content_type='text/plain')
