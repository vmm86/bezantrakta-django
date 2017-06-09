import datetime

from django.db.models import BooleanField, F, Case, When, Value
from django.shortcuts import render

from project.shortcuts import add_small_vertical_poster

from ..models import Event, EventLinkBinder


def event(request, year, month, day, slug):
    """
    Отображение страницы конкретного события

    Логика отображения событий (псевдокод):
    try event: Запрос события в БД для конкретного домена
        ...
    except: События НЕ существует в БД
        [ Ошибка 404 ]
    else: Событие существует в БД
        if event.is_published: Событие опубликовано
            if event.is_coming: Событие опубликовано и ещё НЕ прошло
                [ Вся страница выбора билетов ]
            else: Событие опубликовано и уже прошло
                [ Только общая информация о событии ]
        else: Событие НЕ опубликовано
            if event.is_coming: Событие НЕ опубликовано и ещё НЕ прошло
                [ Ошибка 403 ]
            else: Событие НЕ опубликовано и уже прошло
                [ Ошибка 410 ]
    """
    date = datetime.datetime(year=int(year), month=int(month), day=int(day))
    today = datetime.datetime.today()

    # Запрос события в БД для конкретного домена
    try:
        event = Event.objects.select_related(
            'event_venue',
            'domain'
        ).annotate(
            venue=F('event_venue__title'),
            city=F('domain__city__title'),
            is_coming=Case(
                When(date__gt=today, then=Value(True)),
                default=False,
                output_field=BooleanField()
            ),
        ).values(
            'is_published',
            'is_coming',
            'title',
            'slug',
            'description',
            'keywords',
            'text',
            'date',
            'time',
            'venue',
            'city',
        ).get(
            date=date,
            slug=slug,
            domain_id=request.domain_id
        )
    # Событие НЕ существует в БД
    except Event.DoesNotExist:
        context = {
            'title': """Событие не существует""",
            'message': """<p>К сожалению, такого события не существует. 🙁</p>
            <p>👉 <a href="/">Начните поиск с главной страницы</a>.</p>""",
        }
        return render(request, 'empty.html', context, status=404)
    # Событие существует в БД
    else:
        # Событие опубликовано
        if event['is_published']:
            context = {}

            add_small_vertical_poster(request, event)

            # Запрос ссылок в этом событии
            try:
                links = EventLinkBinder.objects.select_related(
                    'event_link',
                    'event',
                    'domain'
                ).annotate(
                    title=F('event_link__title'),
                    img=F('event_link__img')
                ).filter(
                    event__is_published=True,
                    event__date=date,
                    event__slug=slug,
                    event__domain_id=request.domain_id
                ).values(
                    'title',
                    'href',
                    'img'
                )
            # Ссылок нет
            except EventLinkBinder.DoesNotExist:
                pass
            # Ссылки есть
            else:
                context['links'] = links

            context['event'] = event
            return render(request, 'event/event.html', context)
        # Событие НЕ опубликовано
        else:
            # Событие НЕ опубликовано и ещё НЕ прошло
            if event['is_coming']:
                context = {
                    'title': """Событие не опубликовано""",
                    'message': """<p>К сожалению, это событие ещё не опубликовано на сайте.</p>
                    <p>👉 Зайдите позднее или <a href="/">начните поиск с главной страницы</a>.</p>""",
                }
                return render(request, 'empty.html', context, status=403)
            # Событие НЕ опубликовано и уже прошло
            else:
                context = {
                    'title': """Событие не опубликовано""",
                    'message': """<p>К сожалению, это событие уже прошло и снято с публикации. 🙁</p>
                    <p>👉 <a href="/">Начните поиск с главной страницы</a>.</p>""",
                }
                return render(request, 'empty.html', context, status=410)
