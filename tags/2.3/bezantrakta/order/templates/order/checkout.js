{% spaceless %}
$(document).ready(function(){
    window.expires = new Date(new Date().getTime() + 60 * 60 * 24 * 366 * 1000);
    window.domain = '.{{ request.root_domain }}';
    window.event_uuid = '{{ event.event_uuid }}';
    window.ticket_service_id = '{{ ticket_service.id }}';


    window.event_id = {{ event.ticket_service_event }};

    window.heartbeat_id = undefined;
    {# Таймаут для повторения запроса списка мест в событии #}
    window.heartbeat_timeout = {{ ticket_service.settings.heartbeat_timeout }} * 1000;
    {# Таймаут для выделения места, по истечении которого место автоматически освобождается #}
    window.seat_timeout = {{ ticket_service.settings.seat_timeout }};
    {# Текущий средний совокупный таймаут всех билетов в заказе #}
    window.order_timeout = window.seat_timeout * 60 * 1000;

    window.order_uuid = Cookies.get('bezantrakta_order_uuid');
    window.order_tickets = Cookies.getJSON('bezantrakta_order_tickets');
    window.order_count = parseInt(Cookies.get('bezantrakta_order_count'));
    window.order_total = Math.round(parseFloat(Cookies.get('bezantrakta_order_total')) * 100) / 100;

    {# Стоимость доставки курьером #}
    window.courier_price = Math.round(parseFloat('{{ courier_price }}') * 100) / 100;
    {# Общая сумма заказа со стоимостью доставки курьером #}
    window.order_total_plus_courier_price = Math.round(parseFloat(window.order_total + window.courier_price) * 100) / 100;
    window.commission = {{ commission }};
    {# Общая сумма заказа с комиссией сервиса онлайн-оплаты #}
    window.order_total_plus_commission = Math.round(parseFloat(window.order_total + ((window.order_total * commission) / 100)) * 100) / 100;

// total + ((total * commission) / 100)

    {# Модификация работы с cookie, чтобы избежать ненужного urlendoding #}
    cookies = Cookies.withConverter({
        read: function (value, name) {
            return value;
        },
        write: function (value, name) {
            return value;
        }
    });

    {# Периодическая проверка состояния мест в заказе. #}
    function heartbeat() {
        check_order();
    }

    function start_heartbeat() {
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

    {# При загрузке страницы #}
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

        var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

        var ticket_title = seat['sector_title'] + ',\n' +
                'ряд '   + seat['row_id']       + ',\n' +
                'место ' + seat['seat_title']   + ',\n' +
                'цена '  + seat['price'];

        $('#chosen-tickets').append(
            "<li id=\"" + ticket_id + "\">" +
            '<span id="' + ticket_id + '-countdown" class="countdown"></span> ' +
            ticket_title +
            ' <img class="ruble" src="/static/global/ico/ruble_sign.svg">' +
            '</li>'
        );

        $('#' + ticket_id + '-countdown').html(
            '(' + window.seat_timeout + ':00)'
        );
    }

    {# Значение по умолчанию в поле "Адрес доставки" #}
    $('#customer-address').val('{{ customer.address }}');

    {# При начальной загрузке страницы скрытие всех блоков, появляющихся при выборе чекбоксов #}
    $('#overall-courier,  #overall-online, .ticket-offices-contacts, .customer-address, .payment-info, .eticket-info').hide();

    is_agree();
    $('#agree').change(function(){
        is_agree();
    });

    {# Логика переключения чекбоксов выбора способа заказа #}
    $('#customer-delivery-self').change(function(){
        $('#overall-courier, #overall-online, .customer-address, .online-info').hide();
        $('.ticket-offices-contacts').show();

        $('#delivery').val('self');
        $('#payment').val('cash');

        cookies.set('bezantrakta_customer_order_type', 'self_cash', {expires: window.expires, domain: window.domain});
        console.log('self:', window.order_total);
    });

    $('#customer-delivery-courier').change(function(){
        $(' #overall-online, .ticket-offices-contacts, .online-info').hide();
        $('#overall-courier, .customer-address').show();

        $('#delivery').val('courier');
        $('#payment').val('cash');

        cookies.set('bezantrakta_customer_order_type', 'courier_cash', {expires: window.expires, domain: window.domain});
        console.log('courier:', window.order_total_plus_courier_price);
    });

    $('#customer-delivery-payment').change(function(){
        $('#overall-courier, .ticket-offices-contacts, .customer-address').hide();

        $('.eticket-info').hide();
        $('#overall-online, .payment-info').show();

        $('#delivery').val('self');
        $('#payment').val('online');

        cookies.set('bezantrakta_customer_order_type', 'self_online', {expires: window.expires, domain: window.domain});
        console.log('payment:', window.order_total_plus_commission);
    });

    $('#customer-delivery-eticket').change(function(){
        $('#overall-courier, .ticket-offices-contacts, .customer-address').hide();

        $('.payment-info').hide();
        $(' #overall-online, .eticket-info').show();

        $('#delivery').val('email');
        $('#payment').val('online');

        cookies.set('bezantrakta_customer_order_type', 'email_online', {expires: window.expires, domain: window.domain});
        console.log('eticket:', window.order_total_plus_commission);
    });

    $('input[name="customer_order_type"][class="{{ customer.order_type }}"').prop('checked', true);
    $('input[name="customer_order_type"][class="{{ customer.order_type }}"').trigger('change');

    function check_order() {
        var updated = new Date();

        {# Выбранные ранее билеты: #}
        {# ЛИБО сохраняются в заказе, если их таймаут ещё не прошёл. #}
        {# ЛИБО удаляются из корзины заказа, если их таймаут уже прошёл. #}
        if (window.order_count > 0) {
            {# Ранее выбранные билеты выводятся после перезагрузки страницы. #}
            $('#count-chosen').html(window.order_count);
            $('#total-sum').html(window.order_total);

            $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
            $('#overall-text, #buy-tickets').show();

            for(var t = 0; t < window.order_tickets.length; t++) {
                seat = {};
                seat['sector_id']      = window.order_tickets[t]['sector_id'];
                seat['sector_title']   = window.order_tickets[t]['sector_title'];
                seat['row_id']         = window.order_tickets[t]['row_id'];
                seat['seat_id']        = window.order_tickets[t]['seat_id'];
                seat['seat_title']     = window.order_tickets[t]['seat_title'];
                seat['price_group_id'] = window.order_tickets[t]['price_group_id'];
                seat['price']          = window.order_tickets[t]['price'];
                seat['price_order']    = window.order_tickets[t]['price_order'];

                var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

                {# Таймаут для выделения места в миллисекундах #}
                var seat_timeout = window.seat_timeout * 60 * 1000;

                {# Разница между временем обновления мест и временем резерва конкретного места #}
                var added = new Date(window.order_tickets[t]['added']);
                var updated_minus_added = updated - added;
                console.log('order_seat ', ticket_id, 'updated_minus_added: ', updated_minus_added);

                {# Вывод обратного отсчёта до освобождения места #}
                var uma = new Date(seat_timeout - updated_minus_added);
                var min = uma.getMinutes();
                if (min >= 0 && min < 10) {
                    min = '0' + min;
                }
                var sec = uma.getSeconds();
                if (sec >= 0 && sec < 10) {
                    sec = '0' + sec;
                }
                $('#' + ticket_id + '-countdown').html('(' + min + ':' + sec + ')');

                {# Если заданный таймаут для резерва места прошёл - место освобождается #}
                if (updated_minus_added > seat_timeout) {
                    ts_reserve('remove', seat);
                }

                {# Сумма заказа с комиссией по умолчанию #}
                // if ($('#customer-delivery-self').prop('checked') === true) {
                //     $('#total-sum').html(window.order_total);
                // } else if ($('#customer-delivery-courier').prop('checked') === true) {
                //     $('#total-sum').html(window.order_total_plus_courier_price);
                // } else if ($('#customer-delivery-payment').prop('checked') === true ||
                //     $('#customer-delivery-eticket').prop('checked') === true) {
                //     $('#total-sum').html(window.order_total_plus_commission);
                // }
            }
        } else {
            $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
            $('#overall-text, #buy-tickets').hide();

            location.reload();
        }
    }

    function update_order(response) {
        {# Только если ответ предварительный резерв мест завершился успешно. #}
        if (response['success'] === true) {
            seat = {};
            seat['sector_id']      = response['sector_id'];
            seat['sector_title']   = response['sector_title'];
            seat['row_id']         = response['row_id'];
            seat['seat_id']        = response['seat_id'];
            seat['seat_title']     = response['seat_title'];
            seat['price_group_id'] = response['price_group_id'];
            seat['price']          = Math.round(parseFloat(response['price']) * 100) / 100;
            seat['price_order']    = response['price_order'];

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

            var ticket_title = seat['sector_title'] + ',\n' +
                    'ряд '   + seat['row_id']       + ',\n' +
                    'место ' + seat['seat_title']   + ',\n' +
                    'цена '  + seat['price'];

            $('#' + ticket_id).remove();

            for(var t = 0; t < window.order_tickets.length; t++) {
                if(window.order_tickets[t]['seat_id'] == seat['seat_id']) {
                    window.order_tickets.splice(t, 1);
                }
            }
            window.order_count -= 1;
            window.order_total -= seat['price'];

            cookies.set('bezantrakta_event_id',      window.event_id,      {domain: window.domain});
            cookies.set('bezantrakta_order_count',   window.order_count,   {domain: window.domain});
            cookies.set('bezantrakta_order_total',   window.order_total,   {domain: window.domain});
            cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});

            console.log(
                'action', 'remove', '\n',
                'order_count',   window.order_count, '\n',
                'order_total',   window.order_total, '\n',
                'order_tickets', window.order_tickets
            );

            if (window.order_count > 0) {
                $('#count-chosen').html(window.order_count);
                // $('#total-sum').html(window.order_total);

                $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
                $('#overall-text, #buy-tickets').show();
            } else {
                $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
                $('#overall-text, #buy-tickets').hide();

                location.reload();
            }
        } else {
            return false;
        }
    }

{# Валидация полей формы с контактными данными и запоминание их в cookie для будущих заказов #}

    {# Поле "Имя" - каждое слово капитализируется, обрезка лишних пробелов в начале и в конце #}
    $('#customer-name').blur(function() {
        $(this).each(function() {
            var text = $(this).val(),
                split = text.split(' '),
                res = [],
                i,
                len,
                component;
            for (i = 0, len = split.length; i < len; i++) {
                component = split[i];
                res.push(component.substring(0, 1).toUpperCase());
                res.push(component.substring(1).toLowerCase());
                res.push(' ');
            }
            $(this).val(res.join(''));
            $(this).val($.trim($(this).val()));
            cookies.set('bezantrakta_customer_name', $(this).val(), {expires: window.expires, domain: window.domain});
            return $(this).val();
        });
    });

    {# Поле "Телефон" - обрезка лишних пробелов в начале и в конце #}
    $('#customer-phone').blur(function() {
        $(this).val($.trim($(this).val()));
        cookies.set('bezantrakta_customer_phone', $(this).val(), {expires: window.expires, domain: window.domain});
        return $(this).val();
    });

    {# Поле "Email" - контроль ввода правильного email-адреса, обрезка лишних пробелов в начале и в конце #}
    $('#customer-email').blur(function() {
        var test_email = /^\s*[A-Z0-9._%+-]+@([A-Z0-9-]+\.)+[A-Z]{2,4}\s*$/i;
        if (test_email.test(this.value)) {
            $(this).val($.trim($(this).val()));
            cookies.set('bezantrakta_customer_email', $(this).val(), {expires: window.expires, domain: window.domain});
            return $(this).val();
        } else {
            alert('Пожалуйста, укажите правильный email-адрес');
        }
    });

    {# Поле "Адрес" - обрезка лишних пробелов в начале и в конце #}
    $('#customer-address').blur(function() {
        $(this).val($.trim($(this).val()));
        cookies.set('bezantrakta_customer_address', $(this).val(), {expires: window.expires, domain: window.domain});
        return $(this).val();
    });

    {# Логика переключения чекбокса о согласии на обработку персональных данных #}
    function is_agree() {
        if ($('#agree').prop('checked') === true) {
            $('#isubmit').prop('disabled', false);
        } else {
            $('#isubmit').prop('disabled', true);
        }
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
            var seat_timeout_ms = window.seat_timeout * 60 * 1000;

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
                $('#' + ticket_id).remove();
                ts_reserve('remove', seat);
            }

            {# Если средний совокупный таймаут всех билетов в заказе меньше 15 секунд - #}
            {# возможность подтверждения заказа отключается во избежание ошибок #}
            if (window.order_timeout < 15000) {
                $('#agree').prop('disabled', true);
                $('#isubmit').prop('disabled', true);
                console.log('order_timeout is coming...');
            }

            // cookies.set('bezantrakta_event_id',      window.event_id,      {domain: window.domain});
            // cookies.set('bezantrakta_order_count',   window.order_count,   {domain: window.domain});
            // cookies.set('bezantrakta_order_total',   window.order_total,   {domain: window.domain});
            // cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});
        }

        window.order_timeout = order_timeout_ms / window.order_count;
        console.log('order_timeout: ', window.order_timeout);
    }

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

                'csrfmiddlewaretoken': cookies.get('csrftoken'),
            },
            success: update_order,
            error: log_error
        });
        }

    function log_success(data, status) {
        console.log('Success!', '\nStatus: ', status, '\nData: ', data);
    }

    function log_error(data, status, error) {
        console.log('Error!', '\nStatus: ', status, '\nError: ', error, '\nData: ', data.responseText);
    }

    {# Отправка событий для отслеживания заказов в Яндекс.Метрика и Google.Analytics #}
    function eventYandex() {
        yaCounter{{ request.domain_settings.counter.yandex }}.reachGoal('step2');
        console.log('eventYandex');
        return true;
    }

    function eventGoogle() {
        ga('send', 'event', {eventCategory: 'order', eventAction: 'step2'});
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

    document.getElementById('checkout-form').addEventListener('submit', eventsYandexGoogle);
});
{% endspaceless %}