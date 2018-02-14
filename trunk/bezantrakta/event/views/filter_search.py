from django.db.models import F, Q
from django.shortcuts import redirect, render

from project.cache import cache_factory
from project.shortcuts import timezone_now

from ..models import Event


def filter_search(request):
    """Фильтр событий по названию, тегам ``description`` и ``keywords`` и вывод их афиш в позиции ``small_vertical``"""
    text = request.GET.get('text', '')

    today = timezone_now()

    # Поиск по непустому поисковому запросу, иначе - редирект на главную
    if text and text != '':
        # Получение найденных по поисковому запросу событий
        events_found = list(Event.objects.select_related(
            'event_venue',
            'domain'
        ).annotate(
            uuid=F('id'),
        ).values(
            'uuid',
        ).filter(
            Q(is_group=False) &
            Q(is_published=True) &
            (
                Q(event_category__is_published=True) |
                Q(event_category__isnull=True)
            ) &
            (
                Q(title__icontains=text) |
                Q(description__icontains=text) |
                Q(keywords__icontains=text)
            ) &
            Q(datetime__gt=today) &
            Q(domain_id=request.domain_id)
        ).order_by(
            'datetime',
            'title'
        ))

        if events_found:
            for event in events_found:
                # Получение информации о каждом размещённом событии из кэша
                event.update(cache_factory('event', event['uuid']))

        context = {
            'title': 'Поиск',
            'events_found': events_found,
        }

        return render(request, 'event/filter_search.html', context)
    else:
        return redirect('/')
