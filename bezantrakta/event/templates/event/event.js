{% spaceless %}
$(document).ready(function() {

    window.domain = '.{{ request.root_domain }}';
    window.event_uuid = '{{ event.event_uuid }}';
    window.ticket_service_id = '{{ ticket_service.id }}';
    {# Максимальное число билетов в заказе #}
    window.max_seats_per_order = {{ ticket_service.settings.max_seats_per_order }};
    window.event_id = {{ event.ticket_service_event }};
    window.scheme_id = {{ event.ticket_service_scheme }};
    window.heartbeat_id = undefined;
    {# Таймаут для повторения запроса списка мест в событии #}
    window.heartbeat_timeout = {{ ticket_service.settings.heartbeat_timeout }} * 1000;
    {# Таймаут для выделения места, по истечении которого место автоматически освобождается #}
    window.seat_timeout = {{ ticket_service.settings.seat_timeout }};
    {# Кэш запрошенных ранее мест для сравнения с вновь пришедшими местами #}
    window.seats_cache = [];

    {# Модификация работы с cookie, чтобы избежать ненужного urlendoding #}
    cookies = Cookies.withConverter({
        read: function (value, name) {
            return value;
        },
        write: function (value, name) {
            return value;
        }
    });

    {# Получение параметров заказа. #}
    {# Параметры берутся из существующих cookie или создаются в cookie по умолчанию. #}
    {# Единичный заказ действует только в рамках одного события. #}
    {# Поэтому cookie сбросятся, если другие билеты были выбраны в другом событии, но ещё не были заказаны. #}
    if (cookies.get('bezantrakta_event_id') && parseInt(cookies.get('bezantrakta_event_id')) !== window.event_id) {
            cookies.set('bezantrakta_event_uuid', window.event_uuid, {domain: window.domain});

            window.order_uuid = uuid4();
            cookies.set('bezantrakta_order_uuid', window.order_uuid, {domain: window.domain});

            window.order_tickets = [];
            cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});

            window.order_count = 0;
            cookies.set('bezantrakta_order_count', window.order_count, {domain: window.domain});

            window.order_total = 0;
            cookies.set('bezantrakta_order_total', window.order_total, {domain: window.domain});
    } else {
        cookies.set('bezantrakta_event_id', window.event_id, {domain: window.domain});

        if (cookies.get('bezantrakta_event_uuid')) {
            window.event_uuid = cookies.get('bezantrakta_event_uuid');
        } else {
            cookies.set('bezantrakta_event_uuid', window.event_uuid, {domain: window.domain});
        }

        if (cookies.get('bezantrakta_order_uuid')) {
            window.order_uuid = cookies.get('bezantrakta_order_uuid');
        } else {
            window.order_uuid = uuid4();
            cookies.set('bezantrakta_order_uuid', window.order_uuid, {domain: window.domain});
        }

        if (cookies.get('bezantrakta_order_tickets')) {
            window.order_tickets = cookies.getJSON('bezantrakta_order_tickets');
        } else {
            window.order_tickets = [];
            cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});
        }

        if (cookies.get('bezantrakta_order_count')) {
            window.order_count = parseInt(cookies.get('bezantrakta_order_count'));
        } else {
            window.order_count = 0;
            cookies.set('bezantrakta_order_count', window.order_count, {domain: window.domain});
        }

        if (cookies.get('bezantrakta_order_total')) {
            window.order_total = Math.round(parseFloat(cookies.get('bezantrakta_order_total')) * 100) / 100;
        } else {
            window.order_total = 0;
            cookies.set('bezantrakta_order_total', window.order_total, {domain: window.domain});
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
        ts_seats();
    }

    {# Инициализация зала при загрузке страницы. #}
    {# Селектор `#tickets` указан для того, чтобы работали клики по добавляемым на лету схемам отдельных секторов в больших залах #}
    {# Селектор `#tickets`, к которому применяется `.on()`, НЕ должен генерироваться уже после загрузки страницы, будучи при этом родителем для вновь генерируемых элементов. #}
    function start_heartbeat() {
        {# Добавлять и убирать в предварительном резерве можно только доступные к заказу места #}
        $('#tickets').on('click', '.seat.stateF, .seat.stateS', seat_click_handler);

        heartbeat();

        setInterval(countdown_timer, 1000);

        {# Обновление состояния мест по таймауту #}
        window.heartbeat_id = setInterval(heartbeat, window.heartbeat_timeout);
        console.log('heartbeat ' + window.heartbeat_id + ' started');

        return true;
    }

    function stop_heartbeat() {
        clearInterval(window.heartbeat_id);
        console.log('stopped heartbeat = ' + window.heartbeat_id);
    }

    start_heartbeat();

    {# Периодическое обновление мест в зале. #}
    function update_scheme(response) {
        var updated = new Date();

        {# Выбранные ранее билеты: #}
        {# ЛИБО отмечаются на схеме как выделенные, если их таймаут ещё не прошёл. #}
        {# ЛИБО удаляются из корзины заказа и перестают быть выделенными, если их таймаут уже прошёл. #}

        if (window.order_count > 0) {
            $('#count-chosen').html(window.order_count);
            $('#total-sum').html(window.order_total);

            $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
            $('#overall-text, #buy-tickets').show();
        } else {
            $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
            $('#overall-text, #buy-tickets').hide();
        }

        if (response) {
            {# Храним последний пришедший список мест в кэше в памяти. #}
            {# Перерисовываем места на схеме зала, только если их перечень изменился. #}
            if (_.isEqual(window.seats_cache, response) === false) {
                var seats_prev = window.seats_cache;
                var seats_next = response;
                var seats_prev_size = _.isEmpty(seats_prev) ? _.size(seats_next) : _.size(seats_prev);
                var seats_next_size = _.size(seats_next);
                console.log('seats_prev: ', '\n', seats_prev, '\n');
                console.log('seats_next: ', '\n', seats_next, '\n');

                {# Получаем разницу между местами в кэше и новыми местами #}

                {# Число мест осталось прежним, но какие-то места отличаются #}
                {# Выбранные другими места - отключаем, освободившиеся места - включаем #}
                if (seats_prev_size === seats_next_size) {
                    var seats_prev_diff = _.differenceWith(seats_prev, seats_next, _.isEqual);
                    var seats_next_diff = _.differenceWith(seats_next, seats_prev, _.isEqual);
                    update_seats('less', seats_prev_diff);
                    update_seats('more', seats_next_diff);
                {# Число мест уменьшилось #}
                {# Выбранные другими места - отключаем #}
                } else if (seats_prev_size > seats_next_size) {
                    seats_to_update = _.differenceWith(seats_prev, seats_next, _.isEqual);
                    update_seats('less', seats_to_update);
                {# Число мест увеличилось #}
                {# Освободившиеся места - включаем #}
                } else if (seats_prev_size < seats_next_size) {
                    seats_to_update = _.differenceWith(seats_next, seats_prev, _.isEqual);
                    update_seats('more', seats_to_update);
                }

                {# Актуализация кэша мест в памяти #}
                window.seats_cache = seats_next;
                console.log('seats_cache set: ', '\n');
            } else {
                return false;
            }
        } else {
            console.log('Error: ', response);
        }
    }

    {# Обновление только отличающихся мест #}
    function update_seats(seats_diff_state, seats_to_update) {
        console.log('seats_diff_state: ', seats_diff_state);
        console.log('seats_diff_size: ', _.size(seats_to_update));
        console.log('seats_to_update: ', seats_to_update);

        for (var s = 0; s < seats_to_update.length; s++) {
            seat = {};
            seat['sector_id']      = seats_to_update[s]['sector_id'];
            seat['sector_title']   = seats_to_update[s]['sector_title'];
            seat['row_id']         = seats_to_update[s]['row_id'];
            seat['seat_id']        = seats_to_update[s]['seat_id'];
            seat['seat_title']     = seats_to_update[s]['seat_title'];
            seat['price_group_id'] = seats_to_update[s]['price_group_id'];
            seat['price']          = seats_to_update[s]['price'];
            seat['price_order']    = seats_to_update[s]['price_order'];

            var class_f = 'stateF color' + seat['price_order'];
            var class_s = 'stateS';

            var seat_selector = '#tickets .seat'   +
           '[data-sector-id="' + seat['sector_id'] + '"]' +
           '[data-row-id="'    + seat['row_id']    + '"]' +
           '[data-seat-id="'   + seat['seat_id']   + '"]';

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

            var ticket_title = seat['sector_title'] + ',\n' +
                    'ряд '   + seat['row_id']       + ',\n' +
                    'место ' + seat['seat_title']   + ',\n' +
                    'цена '  + seat['price'];

            if (seats_diff_state == 'more') {
                $(seat_selector).addClass(class_f);

                $(seat_selector).attr('data-sector-id',      seat['sector_id']);
                $(seat_selector).attr('data-sector-title',   seat['sector_title']);
                $(seat_selector).attr('data-row-id',         seat['row_id']);
                $(seat_selector).attr('data-seat-id',        seat['seat_id']);
                $(seat_selector).attr('data-seat-title',     seat['seat_title']);
                $(seat_selector).attr('data-price-group-id', seat['price_group_id']);
                $(seat_selector).attr('data-price',          seat['price']);
                $(seat_selector).attr('data-price-order',    seat['price_order']);

                $(seat_selector).attr('title', ticket_title);
            } else if (seats_diff_state == 'less') {
                $(seat_selector).removeClass(class_f);

                $(seat_selector).removeAttr('title');
            }

            {# Логируем обновление мест только после загрузки всех мест при открытии страницы #}
            if (_.isEmpty(window.seats_cache) === false) {
                console.log(
                    'seat_to_update: ', ticket_id, '\n',
                    'seat_class: ', $(seat_selector).attr('class'), '\n',
                    'seat_title: ', ticket_title, '\n'
                );
            }
        }
    }

    {# Изменение состояния места при клике на нём и редактирование корзины заказа в cookie. #}
    function seat_click_handler(event) {
        event.preventDefault();

        seat = {};
        seat['sector_id']      = parseInt($(this).data('sector-id'));
        seat['sector_title']   = $(this).data('sector-title');
        seat['row_id']         = parseInt($(this).data('row-id'));
        seat['seat_id']        = parseInt($(this).data('seat-id'));
        seat['seat_title']     = $(this).data('seat-title');
        seat['price_group_id'] = parseInt($(this).data('price-group-id'));
        seat['price']          = Math.round(parseFloat($(this).data('price')) * 100) / 100;
        seat['price_order']    = parseInt($(this).data('price-order'));

        var action = undefined;

        var class_f = 'stateF color' + seat['price_order'];
        var class_s = 'stateS';

        var seat_selector = '#tickets .seat'   +
       '[data-sector-id="' + seat['sector_id'] + '"]' +
       '[data-row-id="'    + seat['row_id']    + '"]' +
       '[data-seat-id="'   + seat['seat_id']   + '"]';

        var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

        var ticket_title = seat['sector_title'] + ',\n' +
                'ряд '   + seat['row_id']       + ',\n' +
                'место ' + seat['seat_title']   + ',\n' +
                'цена '  + seat['price'];

        {# Если выбираем ранее невыделенное место - добавляем его в резерв #}
        if ($(this).hasClass(class_f)) {
            {# Нельзя выбрать больше билетов, чем максимальное значение из настроек сервиса продажи билетов #}
            if (window.order_count < window.max_seats_per_order) {
                action = 'add';

                var added = new Date();

                $(seat_selector).addClass(class_s).removeClass(class_f);

                $('#chosen-tickets').append(
                    '<li id="' + ticket_id + '">' +
                    '<span id="' + ticket_id + '-countdown" class="countdown"></span> ' +
                    ticket_title +
                    ' <img class="ruble" src="/static/global/ico/ruble_sign.svg">' +
                    '</li>'
                );

                window.order_tickets.push({
                    'ticket_uuid': uuid4(),
                    'sector_id': seat['sector_id'],
                    'sector_title': seat['sector_title'],
                    'row_id': seat['row_id'],
                    'seat_id': seat['seat_id'],
                    'seat_title': seat['seat_title'],
                    'price_group_id': seat['price_group_id'],
                    'price': seat['price'],
                    'price_order': seat['price_order'],
                    'added': added
                });
                window.order_count += 1;
                window.order_total += seat['price'];

                var seat_timeout = window.seat_timeout < 10 ? '0' + window.seat_timeout : window.seat_timeout;
                $('#' + ticket_id + '-countdown').html(
                    '(' + seat_timeout + ':00)'
                );
            } else {
                return false;
            }
        {# Если снимаем выделенее с ранее выбранного места - удаляем его из резерва #}
        } else if ($(this).hasClass(class_s)) {
            action = 'remove';

            $(seat_selector).addClass(class_f).removeClass(class_s);

            $('#' + ticket_id).remove();

            for(var s = 0; s < window.order_tickets.length; s++) {
                if(window.order_tickets[s]['seat_id'] == seat['seat_id']) {
                    window.order_tickets.splice(s, 1);
                }
            }
            window.order_count -= 1;
            window.order_total -= seat['price'];
        }

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
            'action', action, '\n',
            'added',  added,  '\n',
            'order_count',   window.order_count, '\n',
            'order_total',   window.order_total, '\n',
            'order_tickets', window.order_tickets
        );

        ts_reserve(action, seat);
    }

    function update_order(response) {
        {# Только если ответ предварительного резерва мест завершился успешно. #}
        if (response['success'] === true) {
            seat = {};
            seat['sector_id']      = parseInt(response['sector_id']);
            seat['sector_title']   = response['sector_title'];
            seat['row_id']         = parseInt(response['row_id']);
            seat['seat_id']        = parseInt(response['seat_id']);
            seat['seat_title']     = response['seat_title'];
            seat['price_group_id'] = parseInt(response['price_group_id']);
            seat['price']          = Math.round(parseFloat(response['price']) * 100) / 100;
            seat['price_order']    = parseInt(response['price_order']);

            console.log('seat: ', seat);

        } else {
            {# Удалить место из предварительного резерва мест. #}
            for(var s = 0; s < window.order_tickets.length; s++) {
                if(window.order_tickets[s]['seat_id'] == seat['seat_id']) {
                    window.order_tickets.splice(s, 1);
                }
            }
            window.order_count -= 1;
            window.order_total -= seat['price'];
        }

        cookies.set('bezantrakta_event_id',      window.event_id,      {domain: window.domain});
        cookies.set('bezantrakta_order_count',   window.order_count,   {domain: window.domain});
        cookies.set('bezantrakta_order_total',   window.order_total,   {domain: window.domain});
        cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});

        if (window.order_count > 0) {
            $('#count-chosen').html(window.order_count);
            $('#total-sum').html(window.order_total);

            $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
            $('#overall-text, #buy-tickets').show();
        } else {
            $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
            $('#overall-text, #buy-tickets').hide();
        }

    }

    function clear_order_if_error() {
        cookies.set('bezantrakta_event_id', window.event_id, {domain: window.domain});

        window.order_uuid = uuid4();
        cookies.set('bezantrakta_order_uuid', window.order_uuid, {domain: window.domain});

        window.order_tickets = [];
        cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});

        window.order_count = 0;
        cookies.set('bezantrakta_order_count', window.order_count, {domain: window.domain});

        window.order_total = 0;
        cookies.set('bezantrakta_order_total', window.order_total, {domain: window.domain});

        if (window.order_count > 0) {
            $('#count-chosen').html(window.order_count);
            $('#total-sum').html(window.order_total);

            $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
            $('#overall-text, #buy-tickets').show();
        } else {
            $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
            $('#overall-text, #buy-tickets').hide();
        }
    }

    {# Ранее выбранные билеты выводятся после перезагрузки страницы. #}
    {# Параметры заказа и кнопка `Оформить` выводятся, только если выбрано хотя бы одно место. #}
    if (window.order_count > 0) {
        $('#count-chosen').html(window.order_count);
        $('#total-sum').html(window.order_total);

        $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
        $('#overall-text, #buy-tickets').show();

        for (var t = 0; t < window.order_tickets.length; t++) {
            seat = {};
            seat['sector_id']      = window.order_tickets[t]['sector_id'];
            seat['sector_title']   = window.order_tickets[t]['sector_title'];
            seat['row_id']         = window.order_tickets[t]['row_id'];
            seat['seat_id']        = window.order_tickets[t]['seat_id'];
            seat['seat_title']     = window.order_tickets[t]['seat_title'];
            seat['price_group_id'] = window.order_tickets[t]['price_group_id'];
            seat['price']          = window.order_tickets[t]['price'];
            seat['price_order']    = window.order_tickets[t]['price_order'];

            var class_f = 'stateF color' + seat['price_order'];
            var class_s = 'stateS';

            var seat_selector = '#tickets .seat'   +
           '[data-sector-id="' + seat['sector_id'] + '"]' +
           '[data-row-id="'    + seat['row_id']    + '"]' +
           '[data-seat-id="'   + seat['seat_id']   + '"]';

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

            var ticket_title = seat['sector_title'] + ',\n' +
                    'ряд '   + seat['row_id']       + ',\n' +
                    'место ' + seat['seat_title']   + ',\n' +
                    'цена '  + seat['price'];

            $(seat_selector).attr('data-sector-id',      seat['sector_id']);
            $(seat_selector).attr('data-sector-title',   seat['sector_title']);
            $(seat_selector).attr('data-row-id',         seat['row_id']);
            $(seat_selector).attr('data-seat-title',     seat['seat_title']);
            $(seat_selector).attr('data-price-group-id', seat['price_group_id']);
            $(seat_selector).attr('data-price',          seat['price']);
            $(seat_selector).attr('data-price-order',    seat['price_order']);

            $(seat_selector).attr('title', ticket_title);

            $('#chosen-tickets').append(
                '<li id="' + ticket_id + '">' +
                '<span id="' + ticket_id + '-countdown" class="countdown"></span> ' +
                ticket_title +
                ' <img class="ruble" src="/static/global/ico/ruble_sign.svg">' +
                '</li>'
            );
        }
    } else {
        $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
        $('#overall-text, #buy-tickets').hide();
    }

    {# Обратный отсчёта до освобождения каждого выбранного места в заказе #}
    function countdown_timer() {
        for(var s = 0; s < window.order_tickets.length; s++) {
            seat = {};
            seat['sector_id']      = window.order_tickets[s]['sector_id'];
            seat['sector_title']   = window.order_tickets[s]['sector_title'];
            seat['row_id']         = window.order_tickets[s]['row_id'];
            seat['seat_id']        = window.order_tickets[s]['seat_id'];
            seat['seat_title']     = window.order_tickets[s]['seat_title'];
            seat['price_group_id'] = window.order_tickets[s]['price_group_id'];
            seat['price']          = window.order_tickets[s]['price'];
            seat['price_order']    = window.order_tickets[s]['price_order'];

            var class_f = 'stateF color' + seat['price_order'];
            var class_s = 'stateS';

            var seat_selector = '#tickets .seat'   +
           '[data-sector-id="' + seat['sector_id'] + '"]' +
           '[data-row-id="'    + seat['row_id']    + '"]' +
           '[data-seat-id="'   + seat['seat_id']   + '"]';

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];
            
            {# Таймаут для выделения места в миллисекундах #}
            var seat_timeout_ms = window.seat_timeout * (60 * 1000);

            {# Разница между временем обновления мест и временем резерва конкретного места #}
            var updated = new Date();
            var added = new Date(window.order_tickets[s]['added']);
            var updated_minus_added_ms = updated - added;

            {# Обратный отсчёт до автоматического освобождения места #}
            var uma = new Date(seat_timeout_ms - updated_minus_added_ms);
            var min = uma.getMinutes();
            if (min >= 0 && min < 10) { min = '0' + min; }
            var sec = uma.getSeconds();
            if (sec >= 0 && sec < 10) { sec = '0' + sec; }
            $('#' + ticket_id + '-countdown').html('(' + min + ':' + sec + ')');

            var order_timeout_ms = seat_timeout_ms - updated_minus_added_ms;

            {# Если заданный таймаут для резерва места прошёл - место освобождается #}
            if (updated_minus_added_ms > seat_timeout_ms) {
                $(seat_selector).addClass(class_f).removeClass(class_s);
                $('#' + ticket_id).remove();
                ts_reserve('remove', seat);
            } else {
                $(seat_selector).addClass(class_s).removeClass(class_f);
            }
        }
    }

    {# Получение списка доступных для продажи билетов в событии сервиса продажи билетов. #}
    function ts_seats() {
        $.ajax({
            url: '/api/ts/seats/',
            type: 'GET',
            data: {
                'ticket_service_id': window.ticket_service_id,
                'event_id':          window.event_id,
                'scheme_id':         window.scheme_id
            },
            success: update_scheme,
            error: clear_order_if_error
        });
    }

    {# Добавление или удаление места в предварительном резерве мест (корзина заказа). #}
    function ts_reserve(action, seat) {
        $.ajax({
            url: '/api/ts/reserve/',
            type: 'POST',
            data: {
                'ticket_service_id': window.ticket_service_id,
                'order_uuid':        window.order_uuid,
                'action':            action,
                'event_id':          window.event_id,
                'sector_id':         seat['sector_id'],
                'sector_title':      seat['sector_title'],
                'row_id':            seat['row_id'],
                'seat_id':           seat['seat_id'],
                'seat_title':        seat['seat_title'],
                'price_group_id':    seat['price_group_id'],
                'price':             seat['price'],
                'price_order':       seat['price_order'],

                'csrfmiddlewaretoken': cookies.get('csrftoken')
            },
            success: update_order,
            error: clear_order_if_error
        });
    }

    {# Генерация случайного уникального UUID. #}
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

    function log_success(data, status) {
        console.log('Success!', '\nStatus: ', status, '\nData: ', data);
    }

    function log_error(data, status, error) {
        console.log('Error!', '\nStatus: ', status, '\nError: ', error, '\nData: ', data.responseText);
    }

    {# Отправка событий для отслеживания заказов в Яндекс.Метрика и Google.Analytics #}
    function eventYandex() {
        yaCounter{{ request.domain_settings.counter.yandex }}.reachGoal('step1');
        console.log('eventYandex');
        return true;
    }

    function eventGoogle() {
        ga('send', 'event', {eventCategory: 'order', eventAction: 'step1'});
        console.log('eventGoogle');
    }

    function eventsYandexGoogle() {
        try {
            eventYandex();
            eventGoogle();
        } catch(e) {
            console.log(e);
        }
    }

    document.getElementById('buy-tickets').addEventListener('click', eventsYandexGoogle);
});
{% endspaceless %}