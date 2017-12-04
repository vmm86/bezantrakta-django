import datetime
import simplejson as json
from decimal import Decimal

from django.conf import settings
from django.db.models import F
from django.shortcuts import redirect, render

from project.shortcuts import message, render_messages, timezone_now

from third_party.payment_service.cache import get_or_set_cache as get_or_set_payment_service_cache

from third_party.ticket_service.cache import get_or_set_cache as get_or_set_ticket_service_cache
from third_party.ticket_service.models import TicketServiceSchemeVenueBinder

from ..cache import get_or_set_cache as get_or_set_event_cache
from ..models import Event, EventGroupBinder, EventLinkBinder
from ..shortcuts import add_small_vertical_poster


def event(request, year, month, day, hour, minute, slug):
    """Отображение страницы конкретного события.

    Шаг 1 процесса заказа билетов - выбор билетов на схеме зала и формирование корзины заказа.

    Схема зала с возможностью выбора билетов подгружается, если конкретное событие привязано к сервису продажи билетов.

    Логика отображения событий (псевдокод):
    ::

        try event:  # Запрос события в БД для конкретного домена
            ...
        except:  # События НЕ существует в БД
            [ Ошибка 404 ]
        else:  # Событие существует в БД
            if event.is_published:  # Событие опубликовано
                if event.is_coming:  # Событие опубликовано и ещё НЕ прошло
                    [ Вся страница выбора билетов ]
                else:  # Событие опубликовано и уже прошло
                    [ Только общая информация о событии ]
            else:  # Событие НЕ опубликовано
                if event.is_coming:  # Событие НЕ опубликовано и ещё НЕ прошло
                    [ Ошибка 403 ]
                else:  # Событие НЕ опубликовано и уже прошло
                    [ Ошибка 410 ]

    Args:
        year (str): Год из даты/времени события (``YYYY``).
        month (str): Месяц из даты/времени события (``MM``).
        day (str): День из даты/времени события (``DD``).
        hour (str): Час из даты/времени события (``HH``).
        minute (str): Минуты из даты/времени события (``MM``).
        slug (str): Псевдоним события.
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

    # Запрос базовой информации о событии в БД
    try:
        event = Event.objects.annotate(
            event_uuid=F('id'),
            payment_service_id=F('ticket_service__payment_service_id'),
        ).values(
            'event_uuid',
            'ticket_service_id',
            'payment_service_id'
        ).get(
            datetime=event_datetime_localized,
            slug=slug,
            domain_id=request.domain_id,
        )
    # Событие НЕ существует в БД
    except Event.DoesNotExist:
        # Сообщение об ошибке
        msgs = [
            message('error', 'К сожалению, такого события не существует. 😞'),
            message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
        ]
        render_messages(request, msgs)
        return redirect('error_404')

    # Событие существует в БД
    else:
        # Кэширование информации о событии, сервисе продажи билетов и сервисе онлайн-оплаты
        event = get_or_set_event_cache(event['event_uuid'])

        # Настройки сервиса продажи билетов
        ticket_service = get_or_set_ticket_service_cache(event['ticket_service_id'])

        # Проверка настроек, которые при отсутствии значений выставляются по умолчанию
        ticket_service_defaults = {
            # Максимальное число билетов в заказе
            'max_seats_per_order': settings.BEZANTRAKTA_DEFAULT_MAX_SEATS_PER_ORDER,
            # Таймаут для повторения запроса списка мест в событии в секундах
            'heartbeat_timeout': settings.BEZANTRAKTA_DEFAULT_HEARTBEAT_TIMEOUT,
            # Таймаут для выделения места в минутах, по истечении которого место автоматически освобождается
            'seat_timeout': settings.BEZANTRAKTA_DEFAULT_SEAT_TIMEOUT,
        }
        for param, value in ticket_service_defaults.items():
            if param not in ticket_service['settings'] or ticket_service['settings'][param] is None:
                ticket_service['settings'][param] = value

        # Настройки сервиса онлайн-оплаты
        payment_service = get_or_set_payment_service_cache(event['payment_service_id'])

        today = timezone_now()
        event_is_coming = True if event['event_datetime'] > today else False

        # Событие находится в группе событий или НЕ находится в группе событий и опубликовано
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
                    venue_scheme = TicketServiceSchemeVenueBinder.objects.values_list('scheme', flat=True).get(
                        ticket_service__domain_id=request.domain_id,
                        ticket_service_scheme_id=event['ticket_service_scheme'],
                    )
                except TicketServiceSchemeVenueBinder.DoesNotExist:
                    pass
                else:
                    context['venue_scheme'] = venue_scheme

            context['event'] = event
            context['event']['is_coming'] = event_is_coming
            context['ticket_service'] = ticket_service
            context['payment_service'] = payment_service
            return render(request, 'event/event.html', context)
        # Событие НЕ опубликовано
        else:
            # Событие НЕ опубликовано и ещё НЕ прошло
            if event_is_coming:
                # Сообщение об ошибке
                msgs = [
                    message('error', 'К сожалению, это событие ещё не опубликовано на сайте. 😞'),
                    message('info', '👉 Зайдите позднее или <a href="/">начните поиск с главной страницы</a>.'),
                ]
                render_messages(request, msgs)
                return redirect('error_403')
            # Событие НЕ опубликовано и уже прошло
            else:
                # Сообщение об ошибке
                msgs = [
                    message('error', 'К сожалению, это событие уже прошло и снято с публикации. 😞'),
                    message('info', '👉 <a href="/">Начните поиск с главной страницы</a>.'),
                ]
                render_messages(request, msgs)
                return redirect('error_410')