from django.shortcuts import render

from project.shortcuts import build_absolute_url


def browserconfig(request):
    context = {
        'logo_070_070': build_absolute_url(request.domain_slug, '/static/global/ico/mstile-70x70.png'),
        'logo_150_150': build_absolute_url(request.domain_slug, '/static/global/ico/mstile-150x150.png'),
        'logo_310_310': build_absolute_url(request.domain_slug, '/static/global/ico/mstile-310x310.png'),
        'logo_310_150': build_absolute_url(request.domain_slug, '/static/global/ico/mstile-310x150.png'),
        'tile_color': '#ffe57f'
    }
    return render(request, 'seo/browserconfig.xml', context, content_type='application/xml')
