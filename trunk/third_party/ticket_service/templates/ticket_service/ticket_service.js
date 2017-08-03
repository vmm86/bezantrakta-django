{% spaceless %}
$(document).ready(function() {
    window.domain = '.{{ request.root_domain }}';
    window.max_seats_per_order = {{ event.ticket_service_settings.max_seats_per_order|default_if_none:"7" }};
    window.ticket_service_id = '{{ event.ticket_service_id }}';
    window.event_uuid = '{{ event.id }}';
    window.event_id = {{ event.ticket_service_event }};
    window.venue_id = {{ event.ticket_service_venue }};
    window.heartbeat_id = undefined;
    window.seats_cache = [];
    window.seats_diff = []

    {# Получение параметров заказа (список билетов, число билетов, общая сумма заказа). #}
    {# Параметры берутся из существующих cookie или создаются в cookie по умолчанию. #}
    {# cookie сбросятся, если какие-то другие билеты были выбраны в другом событии, но ещё не были заказаны. #}
    if (Cookies.get('bezantrakta_event_id') && parseInt(Cookies.get('bezantrakta_event_id')) !== window.event_id) {
            window.order_uuid = uuid4();
            Cookies.set('bezantrakta_order_uuid', window.order_uuid, {domain: window.domain});

            window.order_tickets = [];
            Cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});

            window.order_count = 0;
            Cookies.set('bezantrakta_order_count', window.order_count, {domain: window.domain});

            window.order_total = 0;
            Cookies.set('bezantrakta_order_total', window.order_total, {domain: window.domain});
    } else {
        Cookies.set('bezantrakta_event_id', window.event_id, {domain: window.domain});

        if (Cookies.get('bezantrakta_order_uuid')) {
            window.order_uuid = Cookies.get('bezantrakta_order_uuid');
        } else {
            window.order_uuid = uuid4();
            Cookies.set('bezantrakta_order_uuid', window.order_uuid, {domain: window.domain});
        }

        if (Cookies.get('bezantrakta_order_tickets')) {
            window.order_tickets = Cookies.getJSON('bezantrakta_order_tickets');
        } else {
            window.order_tickets = [];
            Cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});
        }

        if (Cookies.get('bezantrakta_order_count')) {
            window.order_count = parseInt(Cookies.get('bezantrakta_order_count'));
        } else {
            window.order_count = 0;
            Cookies.set('bezantrakta_order_count', window.order_count, {domain: window.domain});
        }

        if (Cookies.get('bezantrakta_order_total')) {
            window.order_total = Math.round(parseFloat(Cookies.get('bezantrakta_order_total')) * 100) / 100;
        } else {
            window.order_total = 0;
            Cookies.set('bezantrakta_order_total', window.order_total, {domain: window.domain});
        }
    }
    console.log(
        'order_uuid',    window.order_uuid,  '\n',
        'order_count',   window.order_count, '\n',
        'order_total',   window.order_total, '\n',
        'order_tickets', window.order_tickets
    );

    {# Периодический запрос состояния мест. #}
    function heartbeat() {
        console.log('heartbeat: ' + window.event_id);

        {# Получение списка билетов в продаже #}
        $.ajax({
            url: '/ts/seats/',
            type: 'GET',
            data: {
                'ticket_service_id': window.ticket_service_id,
                'event_uuid': window.event_uuid,

                'event_id': window.event_id,
                'venue_id': window.venue_id
            },
            success: update_scheme,
            error: log_error
        });
    }

    heartbeat();

    {# Инициализация зала при загрузке страницы и периодический запрос состояния мест. #}
    {# `.stagehall` изменено на `#tickets`, чтобы работали клики по добавляемым на лету схемам отдельных секторов в больших залах #}
    {#  Блок, к которому применяется `.on()`, НЕ должен генерироваться уже после загрузки страницы, будучи при этом родителем для вновь генерируемых элементов. #}
    function start_heartbeat() {
        $('#tickets').on('click', '.seat', seat_click_handler);

        {# Обновление состояния мест по таймауту #}
        // heartbeat();
        window.heartbeat_id = setInterval(heartbeat, 10000);
        console.log("heartbeat " + window.heartbeat_id + " started");

        return true;
    }

    start_heartbeat();

    function stop_heartbeat() {
        clearInterval(window.heartbeat_id);
        console.log("stopped heartbeat = " + window.heartbeat_id);
    }

    {# Периодическое обновление мест в зале. #}
    function update_scheme(response) {
        var class_e = 'stateE color0';

        if (response) {
            var response = response;

            {# Храним список мест в кэше. #}
            {# Перерисовываем места на схеме зала, только если их число или состояние изменилось. #}
            if (_.isEqual(window.seats_cache, response) === false) {
                console.log('response: ', response);
                console.log('seats_cache: ', window.seats_cache);
                // console.log('seats_diff: ', window.seats_diff);

                window.seats_cache = response;
                console.log('seats_cache set');

                $('#tickets .seat').removeClass('stateF').addClass(class_e);

                for (var i = 0; i < response.length; i++) {
                    // console.log(response[i]);
                    var class_f = 'stateF color' + response[i]['price_order'];
                    var sector_id      = response[i]['sector_id'];
                    var sector_title   = response[i]['sector_title'];
                    var row_id         = response[i]['row_id'];
                    var seat_id        = response[i]['seat_id'];
                    var seat_title     = response[i]['seat_title'];
                    var price_group_id = response[i]['price_group_id'];
                    var price          = response[i]['price'];

                    var seat = '#tickets .seat'    +
                               '[data-sector-id="' + sector_id + '"]' +
                               '[data-row-id="'    + row_id    + '"]' +
                               '[data-seat-id="'   + seat_id   + '"]';

                    var title = sector_title + '\n' +
                          'ряд '   + row_id       + '\n' +
                          'место ' + seat_title   + '\n' +
                          'цена '  + price;

                    // console.log($(seat));
                    $(seat).attr('data-sector-id', sector_id);
                    $(seat).attr('data-sector-title', sector_title);
                    $(seat).attr('data-row-id', row_id);
                    $(seat).attr('data-seat-title', seat_title);
                    $(seat).attr('data-price-group-id', price_group_id);
                    $(seat).attr('data-price', price);
                    $(seat).attr('title', title);
                    $(seat).toggleClass(class_e).addClass(class_f);
                }
                console.log('seats updated')
            } else {
                return false;
            }

        {# Выбранные ранее билеты отмечаются на схеме как выделенные. #}
        if (window.order_count > 0) {
            for(var s = 0; s < window.order_tickets.length; s++) {
                var seat = '#tickets .seat'    +
                           '[data-sector-id="' + window.order_tickets[s]['sector_id'] + '"]' +
                           '[data-row-id="'    + window.order_tickets[s]['row_id']    + '"]' +
                           '[data-seat-id="'   + window.order_tickets[s]['seat_id']   + '"]';

                $(seat).removeClass('stateE').removeClass('stateF').addClass('stateS');

                console.log('order_seat ', s+1, ': ',
                            window.order_tickets[s]['sector_id'],
                            window.order_tickets[s]['row_id'],
                            window.order_tickets[s]['seat_id']
                );
            }
        }

        } else {
            $('#tickets .seat').removeClass('stateF').addClass(class_e);
            console.log('Error: ', response);
        }
    }

    {# Изменение состояния места при клике на нём и редактирование корзины заказа в cookie. #}
    function seat_click_handler(event) {
        event.preventDefault();

        var sector_id      = $(this).data('sector-id');
        var sector_title   = $(this).data('sector-title');
        var row_id         = $(this).data('row-id');
        var seat_id        = $(this).data('seat-id');
        var seat_title     = $(this).data('seat-title');
        var price_group_id = $(this).data('price-group-id');
        var price          = $(this).data('price');

        var action = '';

        {# Если выбираем ранее невыделенное место. #}
        if ($(this).hasClass('stateF')) {
            {# Нельзя выбрать больше билетов, чем максимальное значение из настроек #}
            if (window.order_count < window.max_seats_per_order) {
                action = 'add';
            } else {
                return false;
            }
        {# Если снимаем выделенее с ранее выбранного места. #}
        } else if ($(this).hasClass('stateS')) {
            action = 'remove';
        }

        $.ajax({
            url: '/ts/reserve/',
            type: 'POST',
            data: {
                'ticket_service_id': window.ticket_service_id,
                'event_uuid': window.event_uuid,

                'order_uuid': window.order_uuid,
                'action': action,
                'event_id': window.event_id,
                'sector_id': sector_id,
                'sector_title': sector_title,
                'row_id': row_id,
                'seat_id': seat_id,
                'seat_title': seat_title,
                'price_group_id': price_group_id,
                'price': price,

                'csrfmiddlewaretoken': Cookies.get('csrftoken')
            },
            success: update_order,
            error: log_error
        });
    }

    function update_order(response) {
        console.log('reserve_response', response)
        {# Только если ответ предварительный резерв мест завершился успешно. #}
        if (response['success'] === true) {
            var action         = response['action'];
            var sector_id      = response['sector_id'];
            var sector_title   = response['sector_title'];
            var row_id         = response['row_id'];
            var seat_id        = response['seat_id'];
            var seat_title     = response['seat_title'];
            var price_group_id = response['price_group_id'];
            var price          = Math.round(parseFloat(response['price']) * 100) / 100;

            var seat = '#tickets .seat' +
                       '[data-sector-id="' + sector_id + '"]' +
                       '[data-row-id="'    + row_id    + '"]' +
                       '[data-seat-id="'   + seat_id   + '"]';

            var ticket_id = sector_id + '-' + row_id + '-' + seat_id;
            var ticket_title = sector_title + ', ряд ' + 
                               row_id       + ', место ' +
                               seat_title   + ', цена ' +
                               price;

            {# Добавить место в предварительный резерв мест. #}
            if (action === 'add') {
                $(seat).toggleClass('stateF').addClass('stateS');

                window.order_tickets.push({
                    'sector_id': sector_id,
                    'sector_title': sector_title,
                    'row_id': row_id,
                    'seat_id': seat_id,
                    'seat_title': seat_title,
                    'price_group_id': price_group_id,
                    'price': price
                });
                $('#chosen-tickets').append(
                    '<li id="' + ticket_id + '">' + ticket_title +
                    ' <img class="ruble" src="/static/global/ico/ruble_sign.svg"></li>'
                );

                window.order_count += 1;
                window.order_total += price;
            {# Удалить место из предварительного резерва мест. #}
            } else if (action === 'remove') {
                $(seat).toggleClass('stateS').addClass('stateF');

                for(var s = 0; s < window.order_tickets.length; s++) {
                    if(window.order_tickets[s]['seat_id'] == seat_id) {
                        window.order_tickets.splice(s, 1);
                    }
                }
                $('#' + ticket_id).remove();

                window.order_count -= 1;
                window.order_total -= price;
            }

            Cookies.set('bezantrakta_event_id',      window.event_id,      {domain: window.domain});
            Cookies.set('bezantrakta_order_count',   window.order_count,   {domain: window.domain});
            Cookies.set('bezantrakta_order_total',   window.order_total,   {domain: window.domain});
            Cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});

            if (window.order_count > 0) {
                $('#count-chosen').html(window.order_count);
                $('#total-sum').html(window.order_total);

                $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
                $('#overall-text, #buy-tickets').show();
            } else {
                $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
                $('#overall-text, #buy-tickets').hide();
            }

            console.log(
                'action',        action,             '\n',
                'order_count',   window.order_count, '\n',
                'order_total',   window.order_total, '\n',
                'order_tickets', window.order_tickets
            );

        } else {
            return false;
        }
    }

    {# Ранее выбранные билеты выводятся после перезагрузки страницы. #}
    {# Параметры заказа и кнопка `Оформить` выводятся, только если выбрано хотя бы одно место. #}
    if (window.order_count > 0) {
        $('#count-chosen').html(window.order_count);
        $('#total-sum').html(window.order_total);

        for (var t = 0; t < window.order_tickets.length; t++) {
            var ticket_id = window.order_tickets[t]['sector_id'] + '-' +
                            window.order_tickets[t]['row_id']    + '-' +
                            window.order_tickets[t]['seat_id'];
            var ticket_title = window.order_tickets[t]['sector_title'] + ', ряд ' +
                               window.order_tickets[t]['row_id'] + ', место ' +
                               window.order_tickets[t]['seat_title'] + ', цена ' +
                               window.order_tickets[t]['price'];
            $('#chosen-tickets').append(
                '<li id="' + ticket_id + '">' + ticket_title +
                ' <img class="ruble" src="/static/global/ico/ruble_sign.svg"></li>'
            );
        }

        $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
        $('#overall-text, #buy-tickets').show();
    } else {
        $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
        $('#overall-text, #buy-tickets').hide();
    }

});

function log_success(data, status) {
    console.log('Success!', '\nStatus: ', status, '\nData: ', data);
}

function log_error(data, status, error) {
    console.log('Error!', '\nStatus: ', status, '\nError: ', error, '\nData: ', data.responseText);
}

function uuid4() {
    var uuid = '', i, random;
    for (i = 0; i < 32; i++) {
        random = Math.random() * 16 | 0;
        if (i == 8 || i == 12 || i == 16 || i == 20) {
            uuid += '-'
        }
        uuid += (i == 12 ? 4 : (i == 16 ? (random & 3 | 8) : random)).toString(16);
    }
    return uuid;
}
{% endspaceless %}