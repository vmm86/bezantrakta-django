import datetime

from django.db.models import F, Q
from django.shortcuts import redirect, render

from project.shortcuts import add_small_vertical_poster

from ..models import Event


def search(request):
    text = request.GET['text']

    if text and text != '':
        today = datetime.datetime.today()

        events = Event.objects.select_related(
            'event_venue',
            'domain'
        ).annotate(
            venue=F('event_venue__title'),
        ).filter(
            Q(title__icontains=text) | Q(description__icontains=text) | Q(keywords__icontains=text),
            is_published=True,
            date__gt=today,
            domain_id=request.domain_id
        ).values(
            'title',
            'slug',
            'date',
            'time',
            'min_price',
            'min_age',
            'venue',
        )

        add_small_vertical_poster(request, events)

        context = {'events': events}

        return render(request, 'event/search.html', context)
    else:
        return redirect('/')
