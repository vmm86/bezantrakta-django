import simplejson as json
import uuid

from django.db.models import F, Q
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from project.shortcuts import datetime_localize_or_utc, ticket_service_instance_cached
from project.urlify import urlify
from bezantrakta.event.models import Event, EventGroupBinder
from third_party.ticket_service.models import TicketService, TicketServiceVenueBinder
from third_party.ticket_service.ticket_service_abc import ticket_service_factory


def seats(request):
    """
    Получение списка мест на запрошенное событие из соответствующего сервиса продажи билетов.
    """
    if request.is_ajax() and request.method == 'GET':
        # Параметры для получения экземпляра класса сервиса продажи билетов
        ticket_service_id = request.GET.get('ticket_service_id')
        event_uuid = request.GET.get('event_uuid')
        # Параметры для получения списка мест в указанном событии/зале
        event_id = request.GET.get('event_id')
        venue_id = request.GET.get('venue_id')

        ts = ticket_service_instance_cached(event_uuid, ticket_service_id)

        seats = ts.seats(
            event_id=event_id,
            venue_id=venue_id
        )

        return JsonResponse(seats, safe=False)


def reserve(request):
    """
    Добавление или удаление места в предварительном резерве мест (корзина заказа).
    """
    if request.is_ajax() and request.method == 'POST':
        # Параметры для получения экземпляра класса сервиса продажи билетов
        ticket_service_id = request.POST.get('ticket_service_id')
        event_uuid = request.POST.get('event_uuid')

        # Параметры для создания предварительного резерва указанного места
        params = {}
        keys = (
            ('action', str,),
            ('order_uuid', str,),
            ('event_id', int,),
            ('sector_id', int,),
            ('sector_title', str,),
            ('row_id', int,),
            ('seat_id', int,),
            ('seat_title', str,),
            ('price_group_id', int,),
            ('price', str,)
        )
        for k in keys:
            params[k[0]] = request.POST.get(k[0])
            if k[1] is int:
                params[k[0]] = int(params[k[0]]) if params[k[0]] is not None else None

        # Экземпляр класса сервиса продажи билетов
        ts = ticket_service_instance_cached(event_uuid, ticket_service_id)

        # Универсальный метод для работы с предварительным резервом мест
        reserve = ts.reserve(**params)

        # Формирование ответа
        response = {}

        if reserve['success']:
            response['success'] = True
            for k in keys:
                response[k[0]] = params[k[0]]
        else:
            response['success'] = False
            response['action'] = params['action']
            response['code'] = reserve['code']
            response['message'] = reserve['message']

        return JsonResponse(response, safe=False)


def discover(request):
    """
    Поиск актуальных залов, событий, групп событий в подключенных к сайтам билетных сервисах.
    Запись полученной информации в соответствующие таблицы базы данных.
    """
    context = {}
    context['ts'] = []
    context['venues'] = []
    context['ts_venue_binder'] = []
    context['ts_venue_binder_dict'] = []
    context['events'] = []
    context['groups_exist'] = []
    context['groups'] = []

    # Активные сервисы продажи билетов
    ticket_services = TicketService.objects.select_related(
        'domain',
        'payment_service'
    ).annotate(
        payment_service_settings=F('payment_service__settings'),
        city_timezone=F('domain__city__timezone'),
    ).values(
        'id',
        'slug',
        'settings',
        'payment_service_id',
        'payment_service_settings',
        'city_timezone',
        'domain_id',
    ).filter(
        Q(is_active=True),
        Q(domain__city__state=True) | Q(domain__city__state=None),
    )

    ticket_services = list(ticket_services)
    context['ticket_services'] = ticket_services

    for ticket_service in ticket_services:
        current_timezone = ticket_service['city_timezone']

        # Получение настроек из JSON
        json_fields = ['settings', 'payment_service_settings', ]  # 'domain_settings'
        for jf in json_fields:
            try:
                ticket_service[jf] = json.loads(ticket_service[jf])
            except TypeError:
                pass

        # Экземпляр класса сервиса продажи билетов для конкретного сайта
        ts = ticket_service_factory(
            ticket_service['slug'],
            ticket_service['settings']['init'],
        )
        context['ts'].append(ts)

        # Залы конкретного сервиса продажи билетов
        venues = ts.discover_venues()
        context['venues'].append(venues)

        # Возможность добавлять из сервиса продажи билетов только те его залы,
        # которые явно принадлежат именно к этому сайту в этом городе
        # (для shared-билетных сервисов между несколькими сайтами).
        # Настройка добавляется администратором по необходимости и используется, только если это непустой список.
        # В противном случае в БД сайта добавляются все залы из сервиса продажи билетов.
        try:
            venues_inclusion_list = (
                ticket_service['settings']['venues'] if
                type(ticket_service['settings']['venues']) is list and
                len(ticket_service['settings']['venues']) > 0 else None
            )
        except KeyError:
            venues_inclusion_list = None

        for v in venues:
            if (
                venues_inclusion_list is None or
                (
                    venues_inclusion_list is not None and
                    v['venue_id'] in venues_inclusion_list
                )
            ):
                try:
                    TicketServiceVenueBinder.objects.create(
                        ticket_service_id=ticket_service['id'],
                        ticket_service_event_venue_id=v['venue_id'],
                        ticket_service_event_venue_title=v['venue_title'],
                    )
                except IntegrityError:
                    pass

        # Залы в модели EventVenue, связанные с залами из сервиса продажи билетов
        ts_venue_binder = TicketServiceVenueBinder.objects.filter(
            ticket_service_id=ticket_service['id'],
            ticket_service__domain_id=ticket_service['domain_id'],
            event_venue__isnull=False,
        ).values_list(
            'ticket_service_event_venue_id',
            'event_venue_id',
        )
        ts_venue_binder_dict = dict(ts_venue_binder)
        context['ts_venue_binder'].append(list(ts_venue_binder))
        context['ts_venue_binder_dict'].append(ts_venue_binder_dict)
        print(ticket_service['id'], ' - ts_venue_binder_dict - ', ts_venue_binder_dict)

        # Группы и события из сервиса продажи билетов зарашиваются,
        # только если их залы в сервисе продажи билетов связаны с залами в БД
        if len(ts_venue_binder_dict) > 0:
            # Сохранение групп в БД

            # Группы, ранее добавленные в БД,
            # к которым могут быть привязаны новые события
            groups_exist = Event.objects.filter(
                is_group=True,
                domain_id=ticket_service['domain_id'],
                ticket_service_id=ticket_service['id'],
            ).values(
                'id',
                'ticket_service_event',
            )
            group_id_uuid_mapping = {ge['ticket_service_event']: ge['id'] for ge in groups_exist}
            # context['group_id_uuid_mapping'].append(group_id_uuid_mapping)

            # В БД сохраняются только те группы,
            # залы в сервисе продажи билетов у которых связаны с залами в БД.
            groups = ts.discover_groups()
            context['groups'].append(groups)

            for g in groups:
                if g['venue_id'] in ts_venue_binder_dict.keys():
                    # Получение даты/времени в текущем часовом поясе (с сохранением в БД в UTC)
                    g['group_datetime'] = datetime_localize_or_utc(g['group_datetime'], current_timezone)
                    group_uuid = uuid.uuid4()
                    # Добавление к псевдониму группы идентификатора группы для уникальности
                    slug_num_chars = 64 - (len(str(g['group_id'])) + 1)
                    group_slug = '{title}-{id}'.format(
                        title=urlify(g['group_title'], num_chars=slug_num_chars),
                        id=g['group_id'],
                    )
                    try:
                        Event.objects.create(
                            id=group_uuid,
                            title=g['group_title'],
                            slug=group_slug,
                            description='',
                            keywords='',
                            text=g['group_text'],
                            is_published=False,
                            is_on_index=False,
                            min_price=g['group_min_price'],
                            datetime=g['group_datetime'],
                            event_venue_id=ts_venue_binder_dict[g['venue_id']],
                            domain_id=ticket_service['domain_id'],
                            is_group=True,
                            ticket_service_id=ticket_service['id'],
                            ticket_service_event=g['group_id'],
                            ticket_service_prices=None,
                            ticket_service_venue=None,
                        )
                    except IntegrityError:
                        pass
                    else:
                        group_id_uuid_mapping[g['group_id']] = group_uuid

            # Сохранение событий в БД

            # В БД сохраняются только те события,
            # залы в сервисе продажи билетов у которых связаны с залами в БД.
            events = ts.discover_events()
            context['events'].append(events)

            for e in events:
                if e['venue_id'] in ts_venue_binder_dict.keys():
                    # Получение даты/времени в текущем часовом поясе (с сохранением в БД в UTC)
                    e['event_datetime'] = datetime_localize_or_utc(e['event_datetime'], current_timezone)
                    event_uuid = uuid.uuid4()
                    # Добавление к псевдониму события идентификатора события для уникальности
                    slug_num_chars = 64 - (len(str(e['event_id'])) + 1)
                    event_slug = '{title}-{id}'.format(
                        title=urlify(e['event_title'], num_chars=slug_num_chars),
                        id=e['event_id'],
                    )
                    # Список цен на билеты для легенды схемы зала
                    prices = json.dumps(ts.prices(event_id=e['event_id']))
                    try:
                        Event.objects.create(
                            id=event_uuid,
                            title=e['event_title'],
                            slug=event_slug,
                            description='',
                            keywords='',
                            text=e['event_text'],
                            is_published=False,
                            is_on_index=False,
                            min_price=e['event_min_price'],
                            datetime=e['event_datetime'],
                            event_venue_id=ts_venue_binder_dict[e['venue_id']],
                            domain_id=ticket_service['domain_id'],
                            is_group=False,
                            ticket_service_id=ticket_service['id'],
                            ticket_service_event=e['event_id'],
                            ticket_service_prices=prices,
                            ticket_service_venue=e['venue_id'],
                        )
                    except IntegrityError:
                        pass

                    # Если событие принадлежит ранее добавленной группе - событие привязывается к группе в БД
                    if e['group_id'] in group_id_uuid_mapping.keys():
                        try:
                            EventGroupBinder.objects.create(
                                group_id=group_id_uuid_mapping[e['group_id']],
                                event_id=event_uuid,
                            )
                        except IntegrityError:
                            pass

            context['group_id_uuid_mapping'] = group_id_uuid_mapping

    return render(request, 'ticket_service/empty.html', context)
