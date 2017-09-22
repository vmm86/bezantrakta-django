from django.db.models import F, Q
from django.shortcuts import redirect, render

from project.shortcuts import timezone_now

from ..models import Event
from ..shortcuts import add_small_vertical_poster


def search(request):
    """Фильтр событий по названию, тегам ``description`` и ``keywords`` и вывод их афиш в позиции ``small_vertical``"""
    text = request.GET['text']

    today = timezone_now()

    # Поиск по непустому поисковому запросу, иначе - редирект на главную
    if text and text != '':
        # Получение найденных по поисковому запросу событий
        events_found = Event.objects.select_related(
            'event_venue',
            'domain'
        ).annotate(
            event_title=F('title'),
            event_slug=F('slug'),
            event_datetime=F('datetime'),
            event_min_price=F('min_price'),
            event_min_age=F('min_age'),
            event_venue_title=F('event_venue__title'),
        ).values(
            'event_title',
            'event_slug',
            'event_datetime',
            'event_min_price',
            'event_min_age',
            'event_venue_title',
        ).filter(
            Q(
                Q(is_group=False) &
                Q(is_published=True) &
                Q(event_category__is_published=True) &
                (
                    Q(title__icontains=text) | Q(description__icontains=text) | Q(keywords__icontains=text)
                ),
                Q(event_datetime__gt=today) &
                Q(domain_id=request.domain_id)
            )
        ).order_by(
            'event_datetime',
            'event_title'
        )

        # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
        add_small_vertical_poster(request, events_found)

        context = {
            'title': 'Поиск',
            'events_found': list(events_found),
        }

        return render(request, 'event/search.html', context)
    else:
        return redirect('/')
