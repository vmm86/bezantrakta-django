import datetime
import simplejson as json
from decimal import Decimal

from django.db.models import BooleanField, Case, F, Value, When
from django.shortcuts import render

from project.shortcuts import add_small_vertical_poster, today
from third_party.ticket_service.models import TicketServiceVenueBinder
from ..models import Event, EventGroupBinder, EventLinkBinder


def event(request, year, month, day, hour, minute, slug):
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
    current_timezone = request.city_timezone
    event_datetime = datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
    )
    event_datetime_localized = current_timezone.localize(event_datetime)

    # Запрос события в БД
    try:
        event = Event.objects.select_related(
            'event_venue',
            'domain'
        ).annotate(
            # Общие параметры
            is_coming=Case(
                When(datetime__gt=today, then=Value(True)),
                default=False,
                output_field=BooleanField()
            ),
            is_in_group=Case(
                When(event_groups__isnull=False, then=Value(True)),
                default=False,
                output_field=BooleanField()
            ),
            # Параметры события
            event_title=F('title'),
            event_slug=F('slug'),
            event_datetime=F('datetime'),
            event_description=F('description'),
            event_keywords=F('keywords'),
            event_text=F('text'),
            event_venue_title=F('event_venue__title'),
            event_venue_city=F('event_venue__city__title'),
            # Параметры группы, если событие в неё входит
            group_id=F('event_groups'),
            group_slug=F('event_groups__slug'),
            group_datetime=F('event_groups__datetime'),
            # Сервис продажи билетов
            ticket_service_settings=F('ticket_service__settings'),
        ).values(
            'id',
            'is_published',
            'is_coming',
            'is_in_group',

            'event_title',
            'event_slug',
            'event_datetime',
            'event_description',
            'event_keywords',
            'event_text',
            'event_venue_title',
            'event_venue_city',

            'group_id',
            'group_slug',
            'group_datetime',

            'ticket_service_id',
            'ticket_service_settings',
            'ticket_service_event',
            'ticket_service_venue',
            'ticket_service_prices',
        ).get(
            datetime=event_datetime_localized,
            slug=slug,
            domain_id=request.domain_id,
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
        # Получение настроек сервиса продажи билетов в JSON
        event['ticket_service_settings'] = (
            json.loads(event['ticket_service_settings']) if
            event['ticket_service_settings'] is not None else
            None
        )

        # Событие опубликовано
        if event['is_in_group'] or (not event['is_in_group'] and event['is_published']):
            context = {}

            # Получение ссылок на маленькие вертикальные афиши либо заглушек по умолчанию
            add_small_vertical_poster(request, event)

            # Запрос ссылок в этом событии
            try:
                links = EventLinkBinder.objects.select_related(
                    'event_link',
                    'event',
                    'domain'
                ).annotate(
                    title=F('event_link__title'),
                    img=F('event_link__img'),
                ).filter(
                    event__is_published=True,
                    event__datetime=event_datetime_localized,
                    event__slug=slug,
                    event__domain_id=request.domain_id,
                ).values(
                    'title',
                    'href',
                    'img',
                )
            # Ссылок нет
            except EventLinkBinder.DoesNotExist:
                pass
            # Ссылки есть
            else:
                context['links'] = links

            # Запрос событий в группе, если это событие добавлено в группу
            if event['is_in_group']:
                group_events = EventGroupBinder.objects.select_related(
                    'event',
                    'domain',
                ).annotate(
                    title=F('event__title'),
                    slug=F('event__slug'),
                    datetime=F('event__datetime'),
                    venue=F('event__event_venue__title'),
                ).filter(
                    group=event['group_id'],
                    # event__is_published=True,
                    event__datetime__gt=today,
                    event__domain_id=request.domain_id,
                ).values(
                    'title',
                    'slug',
                    'datetime',
                    'venue',
                    'caption',
                )
                context['group_events'] = list(group_events)

            # Если событие привязано к сервису продажи билетов
            if event['ticket_service_event']:
                # Цены на билеты в событии по возрастанию
                prices = json.loads(event['ticket_service_prices'], parse_float=Decimal)
                # Цены преобразуются в строки, если дробная часть нулевая - выводятся как целые
                prices = [str(p).split('.')[0] if p % 1 == 0 else str(p) for p in prices]
                context['prices'] = prices

                # Схема зала из БД
                try:
                    venue_scheme = TicketServiceVenueBinder.objects.values_list('scheme', flat=True).get(
                        ticket_service__domain_id=request.domain_id,
                        ticket_service_event_venue_id=event['ticket_service_venue'],
                    )
                except TicketServiceVenueBinder.DoesNotExist:
                    pass
                else:
                    context['venue_scheme'] = venue_scheme

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
