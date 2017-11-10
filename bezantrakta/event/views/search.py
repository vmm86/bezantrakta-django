from django.db.models import F, Q
from django.shortcuts import redirect, render

from project.shortcuts import timezone_now

from ..cache import get_or_set_cache as get_or_set_event_cache
from ..models import Event


def search(request):
    """Фильтр событий по названию, тегам ``description`` и ``keywords`` и вывод их афиш в позиции ``small_vertical``"""
    text = request.GET['text']

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
            Q(
                Q(is_group=False) &
                Q(is_published=True) &
                Q(event_category__is_published=True) &
                (
                    Q(title__icontains=text) |
                    Q(description__icontains=text) |
                    Q(keywords__icontains=text)
                ),
                Q(datetime__gt=today) &
                Q(domain_id=request.domain_id)
            )
        ).order_by(
            'datetime',
            'title'
        ))

        if events_found:
            for event in events_found:
                # Получение информации о каждом размещённом событии из кэша
                event.update(get_or_set_event_cache(event['uuid'], 'event'))

        context = {
            'title': 'Поиск',
            'events_found': events_found,
        }

        return render(request, 'event/search.html', context)
    else:
        return redirect('/')
