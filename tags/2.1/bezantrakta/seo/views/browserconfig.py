from django.shortcuts import render


def browserconfig(request):
    context = {
        'host': request.url_domain,
    }
    return render(request, 'seo/browserconfig.xml', context, content_type='application/xml')
