{# Работа с cookies при заказе билетов #}
window.expires = new Date(new Date().getTime() + 60 * 60 * 24 * 366 * 1000);
window.domain  = '.{{ request.root_domain }}';
{# Модификация работы с Cookies, чтобы избежать ненужного urlendoding #}
window.cookies = Cookies.withConverter({
    read:  function (value, name) { return value; },
    write: function (value, name) { return value; }
});

{# Получение базовых параметров для проведения заказа #}
window.event_uuid = '{{ event.event_uuid }}';
window.ticket_service_id = '{{ ticket_service.id }}';
window.event_id = {{ event.ticket_service_event }};
window.countdown_id = undefined;
{% if active == 'step1' %}
    window.scheme_id = {{ event.ticket_service_scheme }};
    window.seats_id = undefined;
{% endif %}

{# Таймаут для повторного запроса списка свободных мест в событии #}
window.heartbeat_timeout = {{ ticket_service.settings.heartbeat_timeout }};
{# Таймаут, по истечении которого добавленное ранее в предварительный резерв место автоматически освобождается #}
window.seat_timeout = {{ ticket_service.settings.seat_timeout }};

{% if active == 'step1' %}
    window.max_seats_per_order = {{ ticket_service.settings.max_seats_per_order }};

    {# На шаге 1 параметры заказа берутся из существующих cookie или создаются в cookie по умолчанию. #}
    {# Единичный заказ действует только в рамках одного события. #}
    {# Поэтому cookie сбросятся, если другие билеты были выбраны в другом событии, но ещё не были заказаны. #}
    if (
        window.cookies.get('bezantrakta_event_id') &&
        parseInt(window.cookies.get('bezantrakta_event_id')) !== window.event_id
    ) {
        {# Попытка удалить предыдущий предварительный резерв из другого события (если он был создан ранее) #}
        {# с помощью `ts_reserve('remove', seat)` с небольшими задержками во избежание возможных ошибок #}
        window.previous_order = {}
        previous_order['tickets'] = window.cookies.getJSON('bezantrakta_order_tickets');
        previous_order['count']   = parseInt(window.cookies.get('bezantrakta_order_count'));
        previous_order['total']   = get_price(window.cookies.get('bezantrakta_order_total'));

        previous_order['ticket_service_id'] = window.cookies.get('bezantrakta_ticket_service_id');
        previous_order['event_id']          = window.cookies.get('bezantrakta_event_id');
        previous_order['order_uuid']        = window.cookies.get('bezantrakta_order_uuid');

        window.previous_order_cleanup = setInterval(previous_order_cleanup, 2000);

        {# Обнуление корзины заказа в новом открытом событии #}
        window.order_uuid    = uuid4();
        window.order_tickets = [];
        window.order_count   = 0;
        window.order_total   = 0;

        order_cookies_update(
            ['ticket_service_id', 'event_uuid', 'event_id', 'order_uuid', 'order_tickets', 'order_count', 'order_total']
        );
    } else {
        order_cookies_init();
    }
{# На шаге 2 просто получаем созданные ранее параметры заказа из cookie #}
{% elif active == 'step2' %}
    window.order_uuid    = window.cookies.get('bezantrakta_order_uuid');
    window.order_tickets = window.cookies.getJSON('bezantrakta_order_tickets');
    window.order_count   = parseInt(window.cookies.get('bezantrakta_order_count'));
    window.order_total   = get_price(window.cookies.get('bezantrakta_order_total'));

    {# Стоимость доставки курьером #}
    window.courier_price = get_price('{{ courier_price }}');
    {# Общая сумма заказа со стоимостью доставки курьером #}
    window.order_total_plus_courier_price = get_price(window.order_total + window.courier_price);
    window.commission = parseFloat({{ commission }});
    {# Общая сумма заказа с комиссией сервиса онлайн-оплаты #}
    window.order_total_plus_commission = get_price(window.order_total, window.commission);

    {# Текущий средний совокупный таймаут всех билетов в предварительном резерве, #}
    {# по истечении которого блокируется подтверждение заказа на шаге 2 #}
    window.order_timeout = window.seat_timeout * 60 * 1000;
{% endif %}

{# Кэш запрошенных ранее списка цен и свободных мест для сравнения с вновь пришедшими свободными местами #}
window.prices_cache = [];
window.seats_cache = [];

function prepare_order_onload() {
    if (window.order_count > 0) {
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

            var class_f = 'free color' + seat['price_order'];
            var class_s = 'selected';

            var seat_selector = '.seat' +
            '[data-sector-id="' + seat['sector_id'] + '"]' +
            '[data-row-id="'    + seat['row_id']    + '"]' +
            '[data-seat-id="'   + seat['seat_id']   + '"]';

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

            var ticket_title = seat['sector_title'] + ',\n' +
                    'ряд '   + seat['row_id']       + ',\n' +
                    'место ' + seat['seat_title']   + ',\n' +
                    'цена '  + seat['price'] * 1;

            var seat_timeout_output = window.seat_timeout < 10 ? '0' + window.seat_timeout : window.seat_timeout;
            $('#chosen-tickets').append(
                '<li id="'   + ticket_id + '">' +
                '<span id="' + ticket_id + '-countdown" class="countdown">(' + seat_timeout_output + ':00)</span> ' +
                ticket_title + ' <img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">' +
                '</li>'
            );

            {# Выбранные места на схеме зала отмечаются, только если мы на шаге 1 со схемой зала #}
            {% if active == 'step1' %}
                $(seat_selector).addClass(class_s).removeClass(class_f);

                $(seat_selector).attr('data-sector-id',      seat['sector_id']);
                $(seat_selector).attr('data-sector-title',   seat['sector_title']);
                $(seat_selector).attr('data-row-id',         seat['row_id']);
                $(seat_selector).attr('data-seat-title',     seat['seat_title']);
                $(seat_selector).attr('data-price-group-id', seat['price_group_id']);
                $(seat_selector).attr('data-price',          seat['price']);
                $(seat_selector).attr('data-price-order',    seat['price_order']);

                $(seat_selector).attr('title', ticket_title + ' ₽');
            {% endif %}
        }
    }

    html_basket_update();

    {# Работа с секторами в больших или составных залах #}
    {% if active == 'step1' and venue_scheme_sectors %}
        {# Показ выбранного сектора и скрытие всех НЕвыбранных секторов при переключении радиокнопок #}
        $('input[name="sectors"]').change(sectors_handler);
        $('input[name="sectors"]').trigger('change');
    {% endif %}

    {# Подготовка полей формы для подтверждения заказа на шаге 2 #}
    {% if active == 'step2' %}
        {# При начальной загрузке страницы скрытие всех блоков, появляющихся при выборе чекбоксов #}
        $('#overall-courier,  #overall-online, .ticket-offices-contacts, .customer-address, .payment-info, .eticket-info').hide();

        {# Логика переключения чекбоксов при выборе способа заказа #}
        var checkout_options = {
            'self_cash': {
                'field':    '#customer-delivery-self',
                'hide':     '#overall-courier, #overall-online, .customer-address, .online-info',
                'show':     '.ticket-offices-contacts',
                'delivery': 'self',
                'payment':  'cash',
                'total':    window.order_total
            },
            'courier_cash': {
                'field':    '#customer-delivery-courier',
                'hide':     '#overall-online, .ticket-offices-contacts, .online-info',
                'show':     '#overall-courier, .customer-address',
                'delivery': 'courier',
                'payment':  'cash',
                'total':    window.order_total_plus_courier_price
            },
            'self_online': {
                'field':    '#customer-delivery-payment',
                'hide':     '#overall-courier, .ticket-offices-contacts, .customer-address, .eticket-info',
                'show':     '#overall-online, .payment-info',
                'delivery': 'self',
                'payment':  'online',
                'total':    window.order_total_plus_commission
            },
            'email_online': {
                'field':    '#customer-delivery-eticket',
                'hide':     '#overall-courier, .ticket-offices-contacts, .customer-address, .payment-info',
                'show':     '#overall-online, .eticket-info',
                'delivery': 'email',
                'payment':  'online',
                'total':    window.order_total_plus_commission
            }
        };

        $.each(checkout_options, function(option) {
            $(checkout_options[option]['field']).change(function(){
                $(checkout_options[option]['hide']).hide();
                $(checkout_options[option]['show']).show();

                $('#delivery').val(checkout_options[option]['delivery']);
                $('#payment').val(checkout_options[option]['payment']);

                cookies.set('bezantrakta_customer_order_type', option, {expires: window.expires, domain: window.domain});
                {% if debug %}
                    console.log(option, ': ', checkout_options[option]['total']);
                {% endif %}
            });
        });

        {# Выбор последнего варианта заказа билетов, который выбирал покупатель #}
        $('input[name="customer_order_type"][class="{{ customer.order_type }}"').prop('checked', true);
        $('input[name="customer_order_type"][class="{{ customer.order_type }}"').trigger('change');

        {# Значение по умолчанию в поле "Адрес доставки" #}
        $('#customer-address').val('{{ customer.address }}');

        is_agree();
        $('#agree').change(is_agree);

        {# Блокировка повторной отправки формы при подтверждении заказа #}
        $('#checkout-form').submit(function() {
            $(this).find('#submit').prop('disabled', true);
        });

        {# Валидация полей формы с контактными данными на шаге 2 и запоминание их в cookie для будущих заказов #}
        {# Поле "Имя" #}
        {# Каждое слово капитализируется, обрезка лишних пробелов в начале и в конце #}
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
                window.cookies.set('bezantrakta_customer_name', $(this).val(), {expires: window.expires, domain: window.domain});
                return $(this).val();
            });
        });

        {# Поле "Телефон" #}
        {# Обрезка лишних пробелов в начале и в конце #}
        $('#customer-phone').blur(function() {
            $(this).val($.trim($(this).val()));
            window.cookies.set('bezantrakta_customer_phone', $(this).val(), {expires: window.expires, domain: window.domain});
            return $(this).val();
        });

        {# Поле "Email" #}
        {# Контроль ввода правильного email-адреса, обрезка лишних пробелов в начале и в конце #}
        $('#customer-email').blur(function() {
            var test_email = /^\s*[A-Z0-9._%+-]+@([A-Z0-9-]+\.)+[A-Z]{2,4}\s*$/i;
            if (test_email.test(this.value)) {
                $(this).val($.trim($(this).val()));
                window.cookies.set('bezantrakta_customer_email', $(this).val(), {expires: window.expires, domain: window.domain});
                return $(this).val();
            } else {
                alert('Пожалуйста, укажите правильный email-адрес');
            }
        });

        {# Поле "Адрес" #}
        {# Обрезка лишних пробелов в начале и в конце #}
        $('#customer-address').blur(function() {
            $(this).val($.trim($(this).val()));
            window.cookies.set('bezantrakta_customer_address', $(this).val(), {expires: window.expires, domain: window.domain});
            return $(this).val();
        });
    {% endif %}
}

{# Показ выбранного сектора и скрытие всех НЕвыбранных секторов #}
function sectors_handler() {
    {# Скрытие каждого из секторов по умолчанию #}
    $('.sectors-slider .sectors').hide();

    sector_scheme = '.sectors-slider > .' + $(this).attr('id');
    if ($(this).is(':checked')) {
        {% if debug %}console.log(sector_scheme, 'checked');{% endif %}
        $(sector_scheme).show();
    }
}

{# AJAX-запрос к внутреннему API сервисов продажи билетов #}
{# Периодическое получение списка доступных для продажи билетов в событии из сервиса продажи билетов. #}
function ts_seats_and_prices() {
    {% if debug %}
    if (window.seats_id !== undefined) {console.log('ts_seats: ', window.seats_id);}
    {% endif %}

    $.ajax({
        url: '/api/ts/seats_and_prices/',
        type: 'GET',
        data: {
            'ticket_service_id': window.ticket_service_id,
            'event_id':          window.event_id,
            'scheme_id':         window.scheme_id
        },
        success: seats_and_prices_success,
        error: seats_and_prices_error
    });
}

{# AJAX-запрос к внутреннему API сервисов продажи билетов #}
{# Добавление или удаление места в предварительном резерве #}
function ts_reserve(action, seat) {
    $.ajax({
        url: '/api/ts/reserve/',
        type: 'POST',
        data: {
            'ticket_service_id': seat['ticket_service_id'], /* window.ticket_service_id */
            'order_uuid':        seat['order_uuid'], /* window.order_uuid */
            'action':            action,
            'event_id':          seat['event_id'], /* window.event_id */
            'sector_id':         seat['sector_id'],
            'sector_title':      seat['sector_title'],
            'row_id':            seat['row_id'],
            'seat_id':           seat['seat_id'],
            'seat_title':        seat['seat_title'],
            'price_group_id':    seat['price_group_id'],
            'price':             seat['price'],
            'price_order':       seat['price_order'],

            'csrfmiddlewaretoken': window.cookies.get('csrftoken')
        },
        success: reserve_success,
        error: reserve_error
    });
}

{# Инициализация проверок по таймаутам при загрузке страницы #}
function start_heartbeat() {
    {# Периодические проверки состояния мест с обратным отсчётом до их освобождения #}
    window.countdown_id = setInterval(seat_countdown_timer, 1000);
    {% if debug %}console.log('started countdown ' + window.countdown_id);{% endif %}

    {% if active == 'step1' %}
        {# Прелоадер с прогресс-баром #}
        $('#tickets-preloader').show();

        {# Первый запрос свободных для продажи мест при загрузке страницы #}
        ts_seats_and_prices();

        {# Периодические запросы свободных для продажи мест в событии #}
        window.seats_id = setInterval(ts_seats_and_prices, window.heartbeat_timeout * 1000);
        {% if debug %}console.log('started heartbeat ' + window.seats_id);{% endif %}

        {# Добавлять и убирать в предварительном резерве можно только доступные к заказу места #}
        $('#tickets').on('click', '.seat.free, .seat.selected', seat_click_handler);
        {# Селектор `#tickets` указан для того, чтобы работали клики по схемам отдельных секторов в больших залах, когда эти схемы ещё добавлялись "на лету" в jQuery #}
        {# Селектор `#tickets`, к которому применяется `.on()`, НЕ должен генерироваться уже после загрузки страницы, будучи при этом родителем для вновь генерируемых элементов #}

        {# Отключение запроса мест при переходе на шаг 2 #}
        {# (чтобы очередной запуск `ts_seats_and_prices` не мог бы завершился с ошибкой) #}
        $('#buy-tickets').on('click', stop_heartbeat);
    {% elif active == 'step2' %}
        {# Отключение проверки состояния мест при уходе назад на шаг 1 или при подтверждении заказа #}
        $('#back').on('click', stop_heartbeat);
        $('#checkout-form').on('submit', stop_heartbeat);
    {% endif %}

    return true;
}

{# Остановка проверок по по таймаутам при достижении определённых условий #}
function stop_heartbeat() {
    {% if active == 'step1' %}
        clearInterval(window.seats_id);
        {% if debug %}console.log('stopped seats_and_prices ' + window.seats_id);{% endif %}
    {% endif %}

    clearInterval(window.countdown_id);
    {% if debug %}console.log('stopped countdown ' + window.countdown_id);{% endif %}
}

{# Фильтрация из вновь полученного списка только тех мест, состояние которых изменилось (выбраны или освобождены). #}
function seats_and_prices_success(response, status, xhr) {
    if (response) {
        {# Вывод списка цен в легенде #}
        if (_.isEqual(window.prices_cache, response['prices']) === false) {
            var prices_prev = window.prices_cache;
            var prices_next = response['prices'];
            var prices_prev_size = _.isEmpty(prices_prev) ? 0 : _.size(prices_prev);
            var prices_next_size = _.size(prices_next);
            {% if debug %}
            console.log('prices_prev_size: ', prices_prev_size);
            console.log('prices_next_size: ', prices_next_size);
            {% endif %}

            {# Получаем разницу между последующим и предыдущим списком цен: #}

            {# 1. Число цен уменьшилось #}
            {# Убираем НЕактуальные цены #}
            if (prices_prev_size > prices_next_size) {
                var prices_diff = _.differenceWith(prices_prev, prices_next, _.isEqual);
                legend_update('less', prices_diff);
            {# 2. Число цен увеличилось #}
            {# Добавляем актуальные цены #}
            } else if (prices_prev_size < prices_next_size) {
                var prices_diff = _.differenceWith(prices_next, prices_prev, _.isEqual);
                legend_update('more', prices_diff);
            }

            {# Обновление кэша списка мест в памяти #}
            window.prices_cache = prices_next;
            {% if debug %}console.log('prices_cache set');{% endif %}
        }

        {# Храним последний предыдущий список мест в кэше в памяти #}
        {# Перерисовываем места на схеме зала, только если последующий список мест отличается от предыдущего #}
        if (_.isEqual(window.seats_cache, response['seats']) === false) {
            var seats_prev = window.seats_cache;
            var seats_next = response['seats'];
            var seats_prev_size = _.isEmpty(seats_prev) ? 0 : _.size(seats_prev);
            var seats_next_size = _.size(seats_next);
            {% if debug %}
            console.log('seats_prev_size: ', seats_prev_size);
            console.log('seats_next_size: ', seats_next_size);
            {% endif %}

            {# Получаем разницу между последующим и предыдущим списком мест: #}

            {# 1. Число мест осталось прежним, но какие-то места отличаются #}
            {# Выбранные другими места - отключаем, освободившиеся места - включаем #}
            if (seats_prev_size === seats_next_size) {
                var seats_prev_diff = _.differenceWith(seats_prev, seats_next, _.isEqual);
                var seats_next_diff = _.differenceWith(seats_next, seats_prev, _.isEqual);
                scheme_update('less', seats_prev_diff);
                scheme_update('more', seats_next_diff);
            {# 2. Число мест уменьшилось #}
            {# Выбранные другими места - отключаем #}
            } else if (seats_prev_size > seats_next_size) {
                var seats_diff = _.differenceWith(seats_prev, seats_next, _.isEqual);
                scheme_update('less', seats_diff);
            {# 3. Число мест увеличилось #}
            {# Освободившиеся места - включаем #}
            } else if (seats_prev_size < seats_next_size) {
                var seats_diff = _.differenceWith(seats_next, seats_prev, _.isEqual);
                scheme_update('more', seats_diff);
            }

            {# Прелоадер с прогресс-баром #}
            if (_.isEmpty(seats_prev)) {
                $('#tickets-preloader').delay(1000).fadeOut(500);
            }

            {# Обновление кэша свободных мест в памяти #}
            window.seats_cache = seats_next;
            {% if debug %}console.log('seats_cache set');{% endif %}
        }
    } else {
        console.log('Error: ', response);
    }
}

function legend_update(prices_diff_state, prices_diff) {
    {% if debug %}console.log('prices_diff: ', prices_diff);{% endif %}
    for (var p = 1; p < prices_diff.length + 1; p++) {
        {# Если мест пришло больше, чем раньше - включаем освободившиеся места #}
        if (prices_diff_state == 'more') {
            $('#legend-extension').append(
                '<li id="price-' + p + '">' +
                    '<span class="box free color' + p + '"></span> ' + (prices_diff[p - 1] * 1) + ' ' +
                    '<img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">&nbsp;' +
                '</li>'
            );
        {# Если мест пришло меньше, чем раньше - отключаем занятые места #}
        } else if (prices_diff_state == 'less') {
            $('#legend-extension #price-' + p).remove();
        }
    }
}

{# Обновление на схеме зала только отличающихся мест #}
function scheme_update(seats_diff_state, seats_diff) {
    {% if debug %}
    console.log('seats_diff_state: ',  seats_diff_state);
    console.log('seats_diff_size: ', _.size(seats_diff));
    {% endif %}

    for (var s = 0; s < seats_diff.length; s++) {
        seat = {};
        seat['sector_id']      = seats_diff[s]['sector_id'];
        seat['sector_title']   = seats_diff[s]['sector_title'];
        seat['row_id']         = seats_diff[s]['row_id'];
        seat['seat_id']        = seats_diff[s]['seat_id'];
        seat['seat_title']     = seats_diff[s]['seat_title'];
        seat['price_group_id'] = seats_diff[s]['price_group_id'];
        seat['price']          = seats_diff[s]['price'];
        seat['price_order']    = seats_diff[s]['price_order'];

        var class_f = 'free color' + seat['price_order'];
        var class_s = 'selected';

        var seat_selector = '.seat' +
        '[data-sector-id="' + seat['sector_id'] + '"]' +
        '[data-row-id="'    + seat['row_id']    + '"]' +
        '[data-seat-id="'   + seat['seat_id']   + '"]';

        var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

        var ticket_title = seat['sector_title'] + ',\n' +
                'ряд '   + seat['row_id']       + ',\n' +
                'место ' + seat['seat_title']   + ',\n' +
                'цена '  + seat['price'] * 1;

        {# Если мест пришло больше, чем раньше - включаем освободившиеся места #}
        if (seats_diff_state == 'more') {
            $(seat_selector).attr('data-sector-id',      seat['sector_id']);
            $(seat_selector).attr('data-sector-title',   seat['sector_title']);
            $(seat_selector).attr('data-row-id',         seat['row_id']);
            $(seat_selector).attr('data-seat-id',        seat['seat_id']);
            $(seat_selector).attr('data-seat-title',     seat['seat_title']);
            $(seat_selector).attr('data-price-group-id', seat['price_group_id']);
            $(seat_selector).attr('data-price',          seat['price']);
            $(seat_selector).attr('data-price-order',    seat['price_order']);

            $(seat_selector).attr('title', ticket_title + ' ₽');

            $(seat_selector).addClass(class_f);

            {% if ticket_service.hide_sold_non_fixed_seats %}
                $(seat_selector).show();
            {% endif %}
        {# Если мест пришло меньше, чем раньше - отключаем занятые места #}
        } else if (seats_diff_state == 'less') {
            $(seat_selector).removeAttr('title');

            $(seat_selector).removeClass(class_f);
        }
    }

    {% if ticket_service.hide_sold_non_fixed_seats %}
        {# Оставить только актуальные кликабельные билеты без мест, если они выводятся в маркированных списках #}
        if ('.non-fixed-seats .seat:not(.free, .selected)'.length) {
            $('.non-fixed-seats .seat:not(.free, .selected)').hide();
        }
    {% endif %}
}

{# Очищение свободных мест на схеме зала при ошибке запроса `ts_seats` #}
function seats_and_prices_error(xhr, status, error) {
    console.log(
        'ts_scheme error!', '\n',
        'xhr',    xhr,      '\n',
        'status', status,   '\n',
        'error',  error
    );

    {# Обнулить кэш запрошенных ранее свободных мест #}
    window.seats_cache = [];

    {# Деактивировать все свободные и выбранные места на схеме зала #}
    $('.seat.free').removeClass('free');
    $('.seat.selected').removeClass('selected');
}

{# Обработка клика на свободном месте в схеме зала #}
function seat_click_handler(event) {
    event.preventDefault();

    if (window.order_count < window.max_seats_per_order) {
        {# Прелоадер с прогресс-баром #}
        $('#tickets-preloader').fadeIn(20);
    }

    seat = {};
    seat['sector_id']      = parseInt($(this).data('sector-id'));
    seat['sector_title']   = $(this).data('sector-title');
    seat['row_id']         = parseInt($(this).data('row-id'));
    seat['seat_id']        = parseInt($(this).data('seat-id'));
    seat['seat_title']     = $(this).data('seat-title');
    seat['price_group_id'] = parseInt($(this).data('price-group-id'));
    seat['price']          = get_price($(this).data('price'));
    seat['price_order']    = parseInt($(this).data('price-order'));

    seat['ticket_service_id'] = window.ticket_service_id;
    seat['event_id']          = window.event_id;
    seat['order_uuid']        = window.order_uuid;

    var action = undefined;

    var class_f = 'free color' + seat['price_order'];
    var class_s = 'selected';

    {# Если выбираем ранее невыделенное место #}
    if ($(this).hasClass(class_f)) {
        {# Нельзя выбрать больше билетов, чем максимальное значение из настроек сервиса продажи билетов #}
        {# Фактически работает как `order_count` <= `max_seats_per_order` #}
        if (window.order_count < window.max_seats_per_order) {
            action = 'add';
        } else {
            return false;
        }
    {# Если снимаем выделенее с ранее выбранного места #}
    } else if ($(this).hasClass(class_s)) {
        action = 'remove';
    }

    ts_reserve(action, seat);
}

{# Обратный отсчёт до освобождения добавленных в предварительный резерв мест #}
function seat_countdown_timer() {
    var updated = new Date();
    {# Таймаут для выделения места в миллисекундах #}
    var seat_timeout_ms = window.seat_timeout * 60 * 1000;
    {% if active == 'step2' %}
        var order_timeout_ms = 0;
    {% endif %}

    {# Выбранные ранее билеты: #}
    {# * ЛИБО сохраняются в заказе, если их таймаут ещё не прошёл #}
    {# * ЛИБО удаляются из корзины заказа, если их таймаут уже прошёл #}
    if (window.order_count > 0) {
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

            seat['ticket_service_id'] = window.ticket_service_id;
            seat['event_id']          = window.event_id;
            seat['order_uuid']        = window.order_uuid;

            var class_f = 'free color' + seat['price_order'];
            var class_s = 'selected';

            var seat_selector = '.seat' +
            '[data-sector-id="' + seat['sector_id'] + '"]' +
            '[data-row-id="'    + seat['row_id']    + '"]' +
            '[data-seat-id="'   + seat['seat_id']   + '"]';

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

            {# Разница между временем обновления мест и временем резерва конкретного места #}
            var added = new Date(window.order_tickets[t]['added']);
            var updated_minus_added_ms = updated - added;

            {# Вывод обратного отсчёта до автоматического освобождения места #}
            var uma = new Date(seat_timeout_ms - updated_minus_added_ms);
            var min = uma.getMinutes();
            if (min >= 0 && min < 10) { min = '0' + min; }
            var sec = uma.getSeconds();
            if (sec >= 0 && sec < 10) { sec = '0' + sec; }
            $('#' + ticket_id + '-countdown').html('(' + min + ':' + sec + ')');

            {# Если заданный таймаут для резерва места прошёл - место освобождается #}
            if (updated_minus_added_ms > seat_timeout_ms) {
                $('#' + ticket_id + '-countdown').html('(00:00)');

                {# При истечении таймаута на резерв единожды запрашиваем удаление из предваиртельного резерва #}
                {# Если удаление не завершится из-за ошибки - место просто удалится из корзины заказа в браузере #}
                if (window.order_tickets[t]['remove_in_progress'] !== true) {
                    window.order_tickets[t]['remove_in_progress'] = true;

                    {% if active == 'step2' %}
                        for (var t = 0; t < window.order_tickets.length; t++) {
                            if (
                                window.order_tickets[t]['sector_id'] == seat['sector_id'] &&
                                window.order_tickets[t]['row_id']    == seat['row_id']    &&
                                window.order_tickets[t]['seat_id']   == seat['seat_id']
                            ) {
                                window.order_tickets.splice(t, 1);
                                window.order_count -= 1;
                                window.order_total -= seat['price'];
                                window.order_total_plus_courier_price = get_price(
                                    window.order_total + window.courier_price
                                );
                                window.order_total_plus_commission = get_price(
                                    window.order_total, window.commission
                                );

                                order_cookies_update(['order_tickets', 'order_count', 'order_total']);

                                $('#' + ticket_id).remove();
                            }
                        }
                    {% endif %}

                    ts_reserve('remove', seat);
                }
            }

            {% if active == 'step2' %}
                order_timeout_ms += seat_timeout_ms - updated_minus_added_ms;

                {# Если средний совокупный таймаут всех билетов в заказе меньше 10 секунд - #}
                {# возможность подтверждения заказа отключается во избежание ошибок #}
                if (window.order_timeout < 10000 && window.order_timeout != 0) {
                    $('#agree, #isubmit').prop('disabled', true);
                    {% if debug %}console.log('order_timeout is coming...');{% endif %}
                }
            {% endif %}
        }

        {% if active == 'step2' %}
        if (window.order_timeout > 0) {
            window.order_timeout = parseInt(order_timeout_ms / window.order_count);
            {% if debug %}console.log('order_timeout: ', window.order_timeout);{% endif %}
        } else {
            window.order_timeout = 0;
        }
        {% endif %}

    {# Если все билеты удалены из предварительного резерва - перезагрузить страницу #}
    } else {
        {% if active == 'step1' %}
            return false;
        {% elif active == 'step2' %}
            stop_heartbeat();

            html_basket_update();

            location.reload();
        {% endif %}
    }
}

{# Редактирование предварительного резерва #}
function reserve_success(response, status, xhr) {
    var is_successful = response['success'];
    var action = response['action'];

    seat = {};
    seat['sector_id']      = parseInt(response['sector_id']);
    seat['sector_title']   = response['sector_title'];
    seat['row_id']         = parseInt(response['row_id']);
    seat['seat_id']        = parseInt(response['seat_id']);
    seat['seat_title']     = response['seat_title'];
    seat['price_group_id'] = parseInt(response['price_group_id']);
    seat['price']          = get_price(response['price']);
    seat['price_order']    = parseInt(response['price_order']);

    var class_f = 'free color' + seat['price_order'];
    var class_s = 'selected';

    var seat_selector = '.seat' +
    '[data-sector-id="' + seat['sector_id'] + '"]' +
    '[data-row-id="'    + seat['row_id']    + '"]' +
    '[data-seat-id="'   + seat['seat_id']   + '"]';

    var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

    var ticket_title = seat['sector_title'] + ',\n' +
            'ряд '   + seat['row_id']       + ',\n' +
            'место ' + seat['seat_title']   + ',\n' +
            'цена '  + seat['price'] * 1;

    {% if debug %}
    console.log(
        'is_successful: ', is_successful,      '\n',
        'action: ',        action,             '\n',
        'seat: ',          seat,               '\n',
        'order_count: ',   window.order_count, '\n',
        'order_total: ',   window.order_total, '\n',
        'order_tickets: ', window.order_tickets
    );
    {% endif %}

    {# Если добавление или удаление места завершолось успешно #}
    if (is_successful) {
        {# Если место добавлено в предварительный резерв #}
        if (action == 'add') {
            var added = new Date();

            window.order_tickets.push({
                'ticket_uuid':    uuid4(),
                'sector_id':      seat['sector_id'],
                'sector_title':   seat['sector_title'],
                'row_id':         seat['row_id'],
                'seat_id':        seat['seat_id'],
                'seat_title':     seat['seat_title'],
                'price_group_id': seat['price_group_id'],
                'price':          seat['price'],
                'price_order':    seat['price_order'],
                'added':          added
            });
            window.order_count += 1;
            window.order_total += seat['price'];
            {% if active == 'step2' %}
                window.order_total_plus_courier_price = get_price(window.order_total + window.courier_price);
                window.order_total_plus_commission = get_price(window.order_total, window.commission);
            {% endif %}

            order_cookies_update(['order_tickets', 'order_count', 'order_total']);

            {% if active == 'step1' %}
                $(seat_selector).addClass(class_s).removeClass(class_f);
            {% endif %}

            $('#chosen-tickets').append(
                '<li id="' + ticket_id + '">' +
                '<span id="' + ticket_id + '-countdown" class="countdown"></span> ' +
                ticket_title + ' <img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">' +
                '</li>'
            );

            var seat_timeout_output = window.seat_timeout < 10 ? '0' + window.seat_timeout : window.seat_timeout;
            $('#' + ticket_id + '-countdown').html('(' + seat_timeout_output + ':00)');
        {# Если место удалено из предварительного резерва #}
        } else if (action == 'remove') {
            for (var t = 0; t < window.order_tickets.length; t++) {
                if (
                    window.order_tickets[t]['sector_id'] == seat['sector_id'] &&
                    window.order_tickets[t]['row_id']    == seat['row_id']    &&
                    window.order_tickets[t]['seat_id']   == seat['seat_id']
                ) {
                    window.order_tickets.splice(t, 1);
                    window.order_count -= 1;
                    window.order_total -= seat['price'];
                    {% if active == 'step2' %}
                        window.order_total_plus_courier_price = get_price(window.order_total + window.courier_price);
                        window.order_total_plus_commission = get_price(window.order_total, window.commission);
                    {% endif %}

                    order_cookies_update(['order_tickets', 'order_count', 'order_total']);

                    {% if active == 'step1' %}
                        $(seat_selector).addClass(class_f).removeClass(class_s);
                    {% endif %}

                    $('#' + ticket_id).remove();
                }
            }
        }
    }
    {# Если добавление или удаление места завершилось НЕуспешно #}
    {# (например, попытка добавить выбранное другим место) - ничего не происходит #}

    html_basket_update();

    {% if active == 'step1' %}
        {# Прелоадер с прогресс-баром #}
        $('#tickets-preloader').delay(500).fadeOut(20);
    {% endif %}
}

function reserve_error(xhr, status, error) {
    console.log(
        'ts_reserve_error!', '\n',
        'xhr',    xhr,       '\n',
        'status', status,    '\n',
        'error',  error
    );

    {% if active == 'step1' %}
        {# Прелоадер с прогресс-баром #}
        $('#tickets-preloader').hide();
    {% endif %}
}

function previous_order_cleanup() {
    if (window.previous_order !== undefined) {
        var cursor = window.previous_order['tickets'].length - 1;

        if (cursor >= 0)  {
            seat = {};
            seat['sector_id']      = window.previous_order['tickets'][cursor]['sector_id'];
            seat['sector_title']   = window.previous_order['tickets'][cursor]['sector_title'];
            seat['row_id']         = window.previous_order['tickets'][cursor]['row_id'];
            seat['seat_id']        = window.previous_order['tickets'][cursor]['seat_id'];
            seat['seat_title']     = window.previous_order['tickets'][cursor]['seat_title'];
            seat['price_group_id'] = window.previous_order['tickets'][cursor]['price_group_id'];
            seat['price']          = window.previous_order['tickets'][cursor]['price'];
            seat['price_order']    = window.previous_order['tickets'][cursor]['price_order'];

            seat['ticket_service_id'] = window.previous_order['ticket_service_id'];
            seat['event_id']          = window.previous_order['event_id'];
            seat['order_uuid']        = window.previous_order['order_uuid'];

            window.previous_order['tickets'].splice(cursor, 1);
            window.previous_order['count'] -= 1;
            window.previous_order['total'] -= seat['price'];

            console.log('remove previous order seat...', seat);
            ts_reserve('remove', seat);
        } else {
            clearInterval(window.previous_order_cleanup);
            window.previous_order = undefined;
        }
    }
}

{# Инициализация параметров заказа из имеющихся cookies для заказе билетов #}
function order_cookies_init() {
    if (window.cookies.get('bezantrakta_event_uuid')) {
        window.event_uuid = window.cookies.get('bezantrakta_event_uuid');
    } else {
        window.cookies.set('bezantrakta_event_uuid', window.event_uuid, {domain: window.domain});
    }

    window.cookies.set('bezantrakta_event_id', window.event_id, {domain: window.domain});

    if (window.cookies.get('bezantrakta_order_uuid')) {
        window.order_uuid = window.cookies.get('bezantrakta_order_uuid');
    } else {
        window.order_uuid = uuid4();
        window.cookies.set('bezantrakta_order_uuid', window.order_uuid, {domain: window.domain});
    }

    if (window.cookies.get('bezantrakta_order_tickets')) {
        window.order_tickets = window.cookies.getJSON('bezantrakta_order_tickets');
    } else {
        window.order_tickets = [];
        window.cookies.set('bezantrakta_order_tickets', window.order_tickets, {domain: window.domain});
    }

    if (window.cookies.get('bezantrakta_order_count')) {
        window.order_count = parseInt(window.cookies.get('bezantrakta_order_count'));
    } else {
        window.order_count = 0;
        window.cookies.set('bezantrakta_order_count', window.order_count, {domain: window.domain});
    }

    if (window.cookies.get('bezantrakta_order_total')) {
        window.order_total = get_price(window.cookies.get('bezantrakta_order_total'));
    } else {
        window.order_total = 0;
        window.cookies.set('bezantrakta_order_total', window.order_total, {domain: window.domain});
    }
}

{# Сохранение или обновление cookies для заказа билетов #}
function order_cookies_update(cookies_list) {
    {% if debug %}console.log('order_cookies_update...');{% endif %}
    var cookie_prefix = 'bezantrakta_';
    var order_cookies = {
        'ticket_service_id': window.ticket_service_id,
        'event_uuid':        window.event_uuid,
        'event_id':          window.event_id,
        'order_uuid':        window.order_uuid,
        'order_count':       window.order_count,
        'order_total':       window.order_total,
        'order_tickets':     window.order_tickets
    }

    for (var input = 0; input < cookies_list.length; input++) {
        for (var cookie in order_cookies) {
            if (cookies_list[input] === cookie) {
                var cookie_title = cookie;
                var cookie_value = order_cookies[cookie];

                window.cookies.set(cookie_prefix + cookie, cookie_value, {domain: window.domain});
                {% if debug %}console.log('cookie `' + cookie_title + '`: ', cookie_value);{% endif %}
            }
        }
    }
}

{# Обновление HTML-описания корзины заказа #}
{# Добавленные в предварительный резерв билеты выводятся в легенде страницы и отмечаются выделенными на схеме зала. #}
{# В противном случае легенда сбрасывается в состояние по умолчанию "пока ничего не выбрано". #}
function html_basket_update() {
    if (window.order_count > 0) {
        $('#count-chosen').html(window.order_count);
        $('#total-sum').html(window.order_total);
        {% if active == 'step2' %}
            $('#total-sum-courier').html(window.order_total_plus_courier_price);
            $('#total-sum-online').html(window.order_total_plus_commission);
        {% endif %}

        $('#no-tickets, #no-overall, #buy-tickets-inactive').hide();
        $('#overall-text, #buy-tickets').show();
    } else {
        $('#no-tickets, #no-overall, #buy-tickets-inactive').show();
        $('#overall-text, #buy-tickets').hide();
    }
}

{# Получение цены как float с двумя знаками после запятой #}
function get_price(price, commission) {
    {# Если комиссия НЕ задана - получаем цену price #}
    if (commission === undefined) {
        return Math.round(parseFloat(price) * 100) / 100;
    {# Если комиссия задана - получаем цену price с учётом commission #}
    } else if (typeof(commission) === 'number' ) {
        return Math.round(parseFloat(price + ((price * commission) / 100)) * 100) / 100;
    }
}

{# Генерация случайного уникального UUID #}
function uuid4() {
    var uuid = '', i, random;
    for (i = 0; i < 32; i++) {
        random = Math.random() * 16 | 0;
        if (i == 8 || i == 12 || i == 16 || i == 20) {
            uuid += '-';
        }
        uuid += (i == 12 ? 4 : (i == 16 ? (random & 3 | 8) : random)).toString(16);
    }
    return uuid;
}

{# Логика переключения чекбокса о согласии на обработку персональных данных #}
function is_agree() {
    var is_agree = $('#agree').prop('checked') === true ? false : true;
    $('#isubmit').prop('disabled', is_agree);
}

function log_success(data, status) {
    console.log('Success!', '\nStatus: ', status, '\nData: ', data);
}

function log_error(data, status, error) {
    console.log('Error!', '\nStatus: ', status, '\nError: ', error, '\nData: ', data.responseText);
}