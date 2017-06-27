from django.db.models import F, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from project.shortcuts import add_small_vertical_poster

from ..models import Event


today = timezone.now()


def search(request):
    text = request.GET['text']

    if text and text != '':
        # Получение найденных по поисковому запросу событий
        events_found = Event.objects.select_related(
            'event_venue',
            'domain'
        ).annotate(
            venue=F('event_venue__title'),
        ).filter(
            Q(title__icontains=text) | Q(description__icontains=text) | Q(keywords__icontains=text),
            is_published=True,
            datetime__gt=today,
            domain_id=request.domain_id
        ).values(
            'title',
            'slug',
            'datetime',
            'min_price',
            'min_age',
            'venue',
        )

        # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
        add_small_vertical_poster(request, events_found)

        context = {'events': events_found}

        return render(request, 'event/search.html', context)
    else:
        return redirect('/')
