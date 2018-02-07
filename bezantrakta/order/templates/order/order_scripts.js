{# Модификация работы с Cookies, чтобы избежать ненужного urlendoding #}
window.cookies = Cookies.withConverter({
    read:  function (value, name) { return value; },
    write: function (value, name) { return value; }
});

{# Получение базовых параметров для проведения заказа #}
window.event_uuid = '{{ event.event_uuid }}';
window.event_id = {{ event.ticket_service_event }};
window.countdown_id = undefined;
{% if active == 'step1' %}
    window.seats_and_prices_id = undefined;
{% endif %}

{# Таймаут для повторного запроса списка свободных мест в событии #}
window.heartbeat_timeout = {{ ticket_service.settings.heartbeat_timeout }};
{# Таймаут, по истечении которого добавленное ранее в предварительный резерв место автоматически освобождается #}
window.seat_timeout = {{ ticket_service.settings.seat_timeout }};

{# Данные покупателя из cookies #}
window.customer = {};

{# Информация о предварительном резерве как потенциальном заказе #}
window.order = {};

order_cookies_init();

{% if active == 'step1' %}
    window.max_seats_per_order = {{ ticket_service.settings.max_seats_per_order }};

    {# Кэш запрошенных ранее списка цен и свободных мест для сравнения с вновь пришедшими свободными местами #}
    window.prices_cache = [];
    window.seats_cache  = [];

{# На шаге 2 просто получаем созданные ранее параметры заказа из cookie #}
{% elif active == 'step2' %}
    {# Стоимость доставки курьером #}
    window.order['courier_price'] = get_price("{{ order.courier_price|stringformat:'.2f' }}");
    {# Процент комиссии сервиса онлайн-оплаты #}
    window.order['commission'] = parseFloat("{{ order.commission|stringformat:'.2f' }}");

    {# Процент сервисного сбора для разных типов заказа #}
    window.order['extra'] = {};
    window.order['extra']['self_cash']    = parseFloat('{{ event.settings.extra.self_cash }}');
    window.order['extra']['courier_cash'] = parseFloat('{{ event.settings.extra.courier_cash }}');
    window.order['extra']['self_online']  = parseFloat('{{ event.settings.extra.self_online }}');
    window.order['extra']['email_online'] = parseFloat('{{ event.settings.extra.email_online }}');

    {# Текущий средний совокупный таймаут всех билетов в предварительном резерве, #}
    {# по истечении которого блокируется подтверждение заказа на шаге 2 #}
    window.order_timeout = window.seat_timeout * 60 * 1000;
    {% if debug %}console.log('order_timeout (initial): ', window.order_timeout);{% endif %}
{% endif %}

function prepare_order_onload() {
    if (window.order['count'] > 0) {
        for (var t = 0; t < window.order['tickets'].length; t++) {
            seat = {};
            seat['sector_id']      = window.order['tickets'][t]['sector_id'];
            seat['sector_title']   = window.order['tickets'][t]['sector_title'];
            seat['row_id']         = window.order['tickets'][t]['row_id'];
            seat['seat_id']        = window.order['tickets'][t]['seat_id'];
            seat['seat_title']     = window.order['tickets'][t]['seat_title'];
            seat['price_group_id'] = window.order['tickets'][t]['price_group_id'];
            seat['price']          = window.order['tickets'][t]['price'];
            seat['price_order']    = window.order['tickets'][t]['price_order'];

            var class_f = 'free color' + seat['price_order'];
            var class_s = 'selected';

            var seat_selector = '.seat' +
            '[data-sector-id="' + seat['sector_id'] + '"]' +
            '[data-row-id="'    + seat['row_id']    + '"]' +
            '[data-seat-id="'   + seat['seat_id']   + '"]';

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

            var ticket_title = seat['sector_id'] != 0 ? (
                           seat['sector_title'] + ',\n' +
                'ряд '   + seat['row_id']       + ',\n' +
                'место ' + seat['seat_title']   + ',\n' +
                'цена '  + seat['price'] * 1
            ) : (
                           seat['sector_title'] + ',\n' +
                'цена '  + seat['price'] * 1
            );

            var seat_timeout_output = window.seat_timeout < 10 ? '0' + window.seat_timeout : window.seat_timeout;
            $('#chosen-tickets').append(
                '<li id="'   + ticket_id + '">' +
                '<span id="' + ticket_id + '-countdown" class="countdown">(' + seat_timeout_output + ':00)</span> ' +
                ticket_title + ' <img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">' +
                '</li>'
            );

            {# Выбранные места на схеме зала отмечаются только на шаге 1 со схемой зала #}
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
        {# Максимальная ширина блока с секторами - текущая ширина общей схемы зала #}
        if ($('.sectors-slider').length) {
            var scheme_width = $('#tickets #stagehall-block .stagehall').width();
            $('.sectors-slider').css('max-width', scheme_width);
        }

        {# Показ выбранного сектора и скрытие всех НЕвыбранных секторов при переключении радиокнопок #}
        $('input[name="sectors"]').change(sectors_handler);
        $('input[name="sectors"]').trigger('change');
    {% endif %}

    {# Подготовка полей формы для подтверждения заказа на шаге 2 #}
    {% if active == 'step2' %}
        {# При начальной загрузке страницы скрытие всех блоков, появляющихся при выборе чекбоксов #}
        $('#overall-block, .ticket-offices-contacts, .customer-address, .payment-info, .eticket-info').hide();

        {# Логика переключения чекбоксов при выборе способа заказа #}
        var order_types = {
            'self_cash': {
                'field':    '#customer-delivery-self',
                'hide':     '.customer-address, .online-info',
                'show':     '.ticket-offices-contacts',
                'delivery': 'self',
                'payment':  'cash'
            },
            'courier_cash': {
                'field':    '#customer-delivery-courier',
                'hide':     '.ticket-offices-contacts, .online-info',
                'show':     '.customer-address',
                'delivery': 'courier',
                'payment':  'cash'
            },
            'self_online': {
                'field':    '#customer-delivery-payment',
                'hide':     '.ticket-offices-contacts, .customer-address, .eticket-info',
                'show':     '.payment-info',
                'delivery': 'self',
                'payment':  'online'
            },
            'email_online': {
                'field':    '#customer-delivery-eticket',
                'hide':     '.ticket-offices-contacts, .customer-address, .payment-info',
                'show':     '.eticket-info',
                'delivery': 'email',
                'payment':  'online'
            }
        };

        $.each(order_types, function(type) {
            $(order_types[type]['field']).change(function(){
                $(order_types[type]['hide']).hide();
                $(order_types[type]['show']).show();

                {# Обновить выбранный тип заказа #}
                window.customer['order_type'] = type;
                window.customer['delivery'] = order_types[type]['delivery'];
                    $('#delivery').val(window.customer['delivery']);
                window.customer['payment'] = order_types[type]['payment'];
                    $('#payment').val(window.customer['payment']);

                order_cookies_update(['customer_order_type']);

                get_overall();

                html_basket_update();

                {% if debug %}
                    console.log('order_type: ', window.customer['order_type'], '\n',
                                'overall: ',    window.order['overall']);
                {% endif %}
            });
        });

        {# Выбор последнего варианта заказа билетов, который выбирал покупатель #}
        $('input[name="customer_order_type"][class="{{ customer.order_type }}"').prop('checked', true);
        $('input[name="customer_order_type"][class="{{ customer.order_type }}"').trigger('change');

        {# Значение по умолчанию в поле "Адрес доставки" #}
        $('#customer-address').val('{{ customer.address }}');

        /* JS */
        is_agree();
        $('#agree').change(is_agree);

        {# Блокировка повторной отправки формы при подтверждении заказа #}
        $('#checkout-form').submit(function() {
            $('#tickets-preloader').show();
            $(this).find('#submit').prop('disabled', true);
            return true;
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
                window.customer['name'] = $(this).val();
                order_cookies_update('customer_name');
                return window.customer['name'];
            });
        });

        {# Поле "Телефон" #}
        {# Обрезка лишних пробелов в начале и в конце #}
        $('#customer-phone').blur(function() {
            $(this).val($.trim($(this).val()));
            window.customer['phone'] = $(this).val();
            order_cookies_update('customer_phone');
            return window.customer['phone'];
        });

        {# Поле "Email" #}
        {# Контроль ввода правильного email-адреса, обрезка лишних пробелов в начале и в конце #}
        $('#customer-email').blur(function() {
            var test_email = /^\s*[A-Z0-9._%+-]+@([A-Z0-9-]+\.)+[A-Z]{2,4}\s*$/i;
            if (test_email.test(this.value)) {
                $(this).val($.trim($(this).val()));
                window.customer['email'] = $(this).val();
                order_cookies_update('customer_email');
                return window.customer['email'];
            } else {
                alert('Пожалуйста, укажите правильный email-адрес');
            }
        });

        {# Поле "Адрес" #}
        {# Обрезка лишних пробелов в начале и в конце #}
        $('#customer-address').blur(function() {
            $(this).val($.trim($(this).val()));
            window.customer['address'] = $(this).val();
            order_cookies_update('customer_address');
            return window.customer['address'];
        });
        /* JS */
    {% endif %}
}

/* JS */
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
/* JS */

/* JS */
{# Инициализация проверок по таймаутам при загрузке страницы #}
function start_heartbeat() {
    {# Периодические проверки состояния мест с обратным отсчётом до их освобождения #}
    window.countdown_id = setInterval(seat_countdown_timer, 1000);
    {% if debug %}console.log('started countdown ' + window.countdown_id);{% endif %}

    {% if active == 'step1' %}
        {# Прелоадер с прогресс-баром #}
        $('#tickets-preloader').show();

        {# Первый запрос свободных для продажи мест при загрузке страницы #}
        ajax_seats_and_prices();

        {# Периодические запросы свободных для продажи мест в событии #}
        window.seats_and_prices_id = setInterval(ajax_seats_and_prices, window.heartbeat_timeout * 1000);
        {% if debug %}console.log('started heartbeat ' + window.seats_and_prices_id);{% endif %}

        {# Добавлять и убирать в предварительном резерве можно только доступные к заказу места #}
        $('#tickets').on('click', '.seat.free, .seat.selected', seat_click_handler);
        {# Селектор `#tickets` указан для того, чтобы работали клики по схемам отдельных секторов в больших залах, когда эти схемы ещё добавлялись "на лету" в jQuery #}
        {# Селектор `#tickets`, к которому применяется `.on()`, НЕ должен генерироваться уже после загрузки страницы, будучи при этом родителем для вновь генерируемых элементов #}

        {# Отключение запроса мест при переходе на шаг 2, #}
        {# чтобы очередной запуск `ajax_seats_and_prices` не мог бы завершился с ошибкой #}
        $('#buy-tickets').on('click', stop_heartbeat);
    {% elif active == 'step2' %}
        {# Отключение проверки состояния мест при уходе назад на шаг 1 или при подтверждении заказа #}
        $('#back').on('click', stop_heartbeat);
        $('#checkout-form').on('submit', stop_heartbeat);
    {% endif %}

    return true;
}
/* JS */

/* JS */
{# Остановка проверок по по таймаутам при достижении определённых условий #}
function stop_heartbeat() {
    {% if active == 'step1' %}
        clearInterval(window.seats_and_prices_id);
        {% if debug %}console.log('stopped seats_and_prices ' + window.seats_and_prices_id);{% endif %}
        $('#tickets-preloader').show();
    {% endif %}

    clearInterval(window.countdown_id);
    {% if debug %}console.log('stopped countdown ' + window.countdown_id);{% endif %}
}
/* JS */

{# AJAX-запрос к внутреннему API сервисов продажи билетов #}
{# Попытка удалить предыдущий предварительный резерв из другого события (если он был создан ранее). #}
function ajax_prev_order_delete(prev_event_id, prev_order_uuid) {
    $.ajax({
        url: '/api/order/prev_order_delete/',
        type: 'POST',
        data: {
            'event_id':   prev_event_id,
            'order_uuid': prev_order_uuid,

            'csrfmiddlewaretoken': window.cookies.get('csrftoken')
        },
        success: ajax_prev_order_delete_success,
        error:   ajax_prev_order_delete_error
    });
}

{# AJAX-запрос к внутреннему API сервисов продажи билетов #}
{# Периодическое получение списка доступных для продажи билетов и списка цен на билеты в событии #}
function ajax_seats_and_prices() {
    {% if debug %}
    if (window.seats_and_prices_id !== undefined) {
        console.log('ajax_seats_and_prices: ', window.seats_and_prices_id);
    }
    {% endif %}

    $.ajax({
        url: '/api/event/seats_and_prices/',
        type: 'GET',
        data: {
            'event_uuid': window.event_uuid
        },
        success: ajax_seats_and_prices_success,
        error:   ajax_seats_and_prices_error
    });
}

{# AJAX-запрос к внутреннему API сервисов продажи билетов #}
{# Добавление или удаление места в предварительном резерве #}
function ajax_reserve(seat, action) {
    $.ajax({
        url: '/api/order/reserve/',
        type: 'POST',
        data: {
            'event_uuid': window.event_uuid,
            'order_uuid': window.order['uuid'],
            'seat':       JSON.stringify(seat),
            'action':     action,

            'csrfmiddlewaretoken': window.cookies.get('csrftoken')
        },
        success: ajax_reserve_success,
        error:   ajax_reserve_error
    });
}

{# Фильтрация из вновь полученного списка только тех мест, состояние которых изменилось (выбраны или освобождены). #}
function ajax_seats_and_prices_success(response, status, xhr) {
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
                prices_list_update('less', prices_diff);
            {# 2. Число цен увеличилось #}
            {# Добавляем актуальные цены #}
            } else if (prices_prev_size < prices_next_size) {
                var prices_diff = _.differenceWith(prices_next, prices_prev, _.isEqual);
                prices_list_update('more', prices_diff);
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
        {# Если последующий список мест НЕ отличается от предыдущего - значит, свободных мест в продаже НЕТ #}
        } else {
            {# Прелоадер с прогресс-баром #}
            if (_.isEmpty(seats_prev)) {
                $('#tickets-preloader').delay(1000).fadeOut(500);
            }
        }
    } else {
        console.log('Error: ', response);
    }
}

function prices_list_update(prices_diff_state, prices_diff) {
    {% if debug %}console.log('prices_diff: ', prices_diff);{% endif %}
    for (var p = 1; p < prices_diff.length + 1; p++) {
        {# Если цен пришло больше, чем раньше - добавляем новые цены #}
        if (prices_diff_state == 'more') {
            $('#legend-extension').append(
                '<li id="price-' + p + '">' +
                    '<span class="box free color' + p + '"></span> ' + (prices_diff[p - 1] * 1) + ' ' +
                    '<img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">&nbsp;' +
                '</li>'
            );
        {# Если цен пришло меньше, чем раньше - удаляем старые цены #}
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
    console.log('seats_diff: ', seats_diff);
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

        var ticket_title = seat['sector_id'] != 0 ? (
                       seat['sector_title'] + ',\n' +
            'ряд '   + seat['row_id']       + ',\n' +
            'место ' + seat['seat_title']   + ',\n' +
            'цена '  + seat['price'] * 1
        ) : (
                       seat['sector_title'] + ',\n' +
            'цена '  + seat['price'] * 1
        );

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
function ajax_seats_and_prices_error(xhr, status, error) {
    console.log(
        'ajax_seats_and_prices_error error!', '\n',
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
function seat_click_handler(click) {
    click.preventDefault();

    if (window.order['count'] < window.max_seats_per_order) {
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

    // seat['ticket_service_id'] = window.ticket_service_id;
    // seat['event_id']          = window.event_id;
    // seat['order_uuid']        = window.order['uuid'];

    var action = undefined;

    var class_f = 'free color' + seat['price_order'];
    var class_s = 'selected';

    {# Если выбираем НЕ выбранное ранее место #}
    if ($(this).hasClass(class_f)) {
        {# Нельзя выбрать больше билетов, чем максимальное значение из настроек сервиса продажи билетов #}
        {# Фактически работает как `order_count` <= `max_seats_per_order` #}
        if (window.order['count'] < window.max_seats_per_order) {
            action = 'add';
        } else {
            return false;
        }
    {# Если снимаем выделенее с ранее выбранного места #}
    } else if ($(this).hasClass(class_s)) {
        action = 'remove';
    }

    ajax_reserve(seat, action);
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
    if (window.order['count'] > 0) {
        for (var t = 0; t < window.order['tickets'].length; t++) {
            seat = {};
            seat['sector_id']      = window.order['tickets'][t]['sector_id'];
            seat['sector_title']   = window.order['tickets'][t]['sector_title'];
            seat['row_id']         = window.order['tickets'][t]['row_id'];
            seat['seat_id']        = window.order['tickets'][t]['seat_id'];
            seat['seat_title']     = window.order['tickets'][t]['seat_title'];
            seat['price_group_id'] = window.order['tickets'][t]['price_group_id'];
            seat['price']          = window.order['tickets'][t]['price'];
            seat['price_order']    = window.order['tickets'][t]['price_order'];

            // seat['ticket_service_id'] = window.ticket_service_id;
            // seat['event_id']          = window.event_id;
            // seat['order_uuid']        = window.order['uuid'];

            var class_f = 'free color' + seat['price_order'];
            var class_s = 'selected';

            var seat_selector = '.seat' +
            '[data-sector-id="' + seat['sector_id'] + '"]' +
            '[data-row-id="'    + seat['row_id']    + '"]' +
            '[data-seat-id="'   + seat['seat_id']   + '"]';

            var ticket_id = seat['sector_id'] + '-' + seat['row_id'] + '-' + seat['seat_id'];

            {# Разница между временем обновления мест и временем резерва конкретного места #}
            var added = new Date(window.order['tickets'][t]['added']);
            var updated_minus_added_ms = updated - added;

            {# Вывод обратного отсчёта до автоматического освобождения места #}
            var uma = new Date(seat_timeout_ms - updated_minus_added_ms);
            var min = uma.getMinutes();
            var sec = uma.getSeconds();
            min = min >= 0 && min < 10 ? '0' + min : min;
            sec = sec >= 0 && sec < 10 ? '0' + sec : sec;
            $('#' + ticket_id + '-countdown').html('(' + min + ':' + sec + ')');

            {# Если заданный таймаут для резерва места прошёл - место освобождается #}
            if (updated_minus_added_ms > seat_timeout_ms) {
                $('#' + ticket_id + '-countdown').html('(00:00)');

                {# При истечении таймаута на резерв ЕДИНОЖДЫ запрашиваем удаление из предварительного резерва #}
                {# Если удаление не завершится из-за ошибки - место просто удалится из корзины заказа в браузере #}
                if (window.order['tickets'][t]['remove_in_progress'] !== true) {
                    window.order['tickets'][t]['remove_in_progress'] = true;

                    {% if active == 'step2' %}
                        for (var t = 0; t < window.order['tickets'].length; t++) {
                            if (
                                window.order['tickets'][t]['sector_id'] == seat['sector_id'] &&
                                window.order['tickets'][t]['row_id']    == seat['row_id']    &&
                                window.order['tickets'][t]['seat_id']   == seat['seat_id']
                            ) {
                                window.order['tickets'].splice(t, 1);
                                window.order['count'] -= 1;
                                window.order['total'] -= seat['price'];

                                order_cookies_update(['order_tickets', 'order_count', 'order_total']);

                                get_overall();

                                $('#' + ticket_id).remove();
                            }
                        }
                    {% endif %}

                    ajax_reserve(seat, 'remove');
                }
        {% if active == 'step2' %}
            } else {
                window.order['tickets'][t]['order_timeout_ms'] = seat_timeout_ms - updated_minus_added_ms;

                {# Временное отключение возможности подтвердить заказ при удалении очередного билета из резерва #}
                if (window.order['tickets'][t]['order_timeout_ms'] < 5000) {
                    $('#agree, #isubmit').prop('disabled', true);
                }

                order_timeout_ms += window.order['tickets'][t]['order_timeout_ms'];
        {% endif %}
            }
        }

        {% if active == 'step2' %}
            window.order_timeout = order_timeout_ms > 0 ? parseInt(order_timeout_ms / window.order['count']) : 11000;
            {% if debug %}console.log('window.order_timeout: ', window.order_timeout);{% endif %}

            {# Если средний совокупный таймаут всех билетов в заказе меньше 10 секунд - #}
            {# возможность подтверждения заказа отключается во избежание ошибок #}
            if (window.order_timeout < 10000) {
                $('#agree, #isubmit').prop('disabled', true);
                {% if debug %}console.log('order_timeout is coming...');{% endif %}
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
function ajax_reserve_success(response, status, xhr) {
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

    var ticket_title = seat['sector_id'] != 0 ? (
                   seat['sector_title'] + ',\n' +
        'ряд '   + seat['row_id']       + ',\n' +
        'место ' + seat['seat_title']   + ',\n' +
        'цена '  + seat['price'] * 1
    ) : (
                   seat['sector_title'] + ',\n' +
        'цена '  + seat['price'] * 1
    );

    {% if debug %}
    console.log(
        'is_successful: ', is_successful,         '\n',
        'action: ',        action,                '\n',
        'seat: ',          seat,                  '\n',
        'order_count: ',   window.order['count'], '\n',
        'order_total: ',   window.order['total'], '\n',
        'order_tickets: ', window.order['tickets']
    );
    {% endif %}

    {# Если операция завершилась успешно #}
    if (is_successful === true) {
        {# Если место добавлено в предварительный резерв #}
        if (action == 'add') {
            var added = new Date();

            window.order['tickets'].push({
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
            window.order['count'] += 1;
            window.order['total'] += seat['price'];

            order_cookies_update(['order_tickets', 'order_count', 'order_total']);

            $('#chosen-tickets').append(
                '<li id="' + ticket_id + '">' +
                '<span id="' + ticket_id + '-countdown" class="countdown"></span> ' +
                ticket_title + ' <img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">' +
                '</li>'
            );

            {% if active == 'step1' %}
                $(seat_selector).addClass(class_s).removeClass(class_f);
            {% elif active == 'step2' %}
                get_overall();
            {% endif %}

            var seat_timeout_output = window.seat_timeout < 10 ? '0' + window.seat_timeout : window.seat_timeout;
            $('#' + ticket_id + '-countdown').html('(' + seat_timeout_output + ':00)');
        {# Если место удалено из предварительного резерва #}
        } else if (action == 'remove') {
            for (var t = 0; t < window.order['tickets'].length; t++) {
                if (
                    window.order['tickets'][t]['sector_id'] == seat['sector_id'] &&
                    window.order['tickets'][t]['row_id']    == seat['row_id']    &&
                    window.order['tickets'][t]['seat_id']   == seat['seat_id']
                ) {
                    window.order['tickets'].splice(t, 1);
                    window.order['count'] -= 1;
                    window.order['total'] -= seat['price'];

                    $('#' + ticket_id).remove();

                    order_cookies_update(['order_tickets', 'order_count', 'order_total']);

                    {% if active == 'step1' %}
                        $(seat_selector).addClass(class_f).removeClass(class_s);
                    {% elif active == 'step2' %}
                        get_overall();
                    {% endif %}
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
    {% elif active == 'step2' %}
        {# Включение возможности подтвердить заказ после удаления очередного билета, если заказ ещё не пустой #}
        var no_tickets = _.isEmpty(window.order['tickets']);
        if (no_tickets === false && window.order_timeout > 10000) {
            $('#agree, #isubmit').prop('disabled', false);
        }
    {% endif %}
}

function ajax_reserve_error(xhr, status, error) {
    console.log(
        'ajax_reserve_error!', '\n',
        'xhr',    xhr,       '\n',
        'status', status,    '\n',
        'error',  error
    );

    {% if active == 'step1' %}
        {# Прелоадер с прогресс-баром #}
        $('#tickets-preloader').hide();
    {% elif active == 'step2' %}
        {# Включение возможности подтвердить заказ после удаления очередного билета, если заказ ещё не пустой #}
        var no_tickets = _.isEmpty(window.order['tickets']);
        if (no_tickets === false && window.order_timeout > 10000) {
            $('#agree, #isubmit').prop('disabled', false);
        }
    {% endif %}
}

function ajax_prev_order_delete_success(response, status, xhr) {
    {% if debug %}console.log('previous order removed: ', response);{% endif %}

    {# Обнуление корзины заказа в новом открытом событии #}
    window.order['uuid']    = uuid4();
    window.order['tickets'] = [];
    window.order['count']   = 0;
    window.order['total']   = 0;
}

function ajax_prev_order_delete_error(xhr, status, error) {
    console.log(
        'ajax_prev_order_delete_error!', '\n',
        'xhr',    xhr,       '\n',
        'status', status,    '\n',
        'error',  error
    );

    {# Обнуление корзины заказа в новом открытом событии #}
    window.order['uuid']    = uuid4();
    window.order['tickets'] = [];
    window.order['count']   = 0;
    window.order['total']   = 0;
}

{# Инициализация параметров заказа из имеющихся cookies для заказе билетов #}
function order_cookies_init() {
    {# На шаге 1 параметры заказа берутся из существующих cookie или создаются в cookie по умолчанию. #}
    {# Единичный заказ действует только в рамках одного события. #}
    {# Поэтому cookie сбросятся, если другие билеты были выбраны в другом событии, но ещё не были заказаны. #}
    if (
        window.cookies.get('bezantrakta_event_id') &&
        parseInt(window.cookies.get('bezantrakta_event_id')) !== window.event_id
    ) {
        {# Попытка удалить предыдущий предварительный резерв из другого события (если он был создан ранее) #}
        {# с небольшими задержками во избежание возможных ошибок #}
        var prev_event_id   = window.cookies.get('bezantrakta_event_id');
        var prev_order_uuid = window.cookies.get('bezantrakta_order_uuid');

        ajax_prev_order_delete(prev_event_id, prev_order_uuid);

        {# Обнуление корзины заказа в новом открытом событии #}
        window.order['uuid']    = uuid4();
        window.order['tickets'] = [];
        window.order['count']   = 0;
        window.order['total']   = 0;
    } else {
        if (window.cookies.get('bezantrakta_event_uuid')) {
            window.event_uuid = window.cookies.get('bezantrakta_event_uuid');
        }

        window.order['ticket_service_id'] = window.cookies.get('bezantrakta_ticket_service_id');

        window.customer['order_type'] = undefined;
        window.customer['name']       = window.cookies.get('bezantrakta_customer_name');
        window.customer['phone']      = window.cookies.get('bezantrakta_customer_phone');
        window.customer['email']      = window.cookies.get('bezantrakta_customer_email');
        window.customer['address']    = window.cookies.get('bezantrakta_customer_address');

        {# Данные о заказе #}
        window.order['uuid'] = window.cookies.get('bezantrakta_order_uuid') ? window.cookies.get('bezantrakta_order_uuid') : uuid4();
        window.order['tickets'] = window.cookies.get('bezantrakta_order_tickets') ? window.cookies.getJSON('bezantrakta_order_tickets') : [];
        window.order['count'] = window.cookies.get('bezantrakta_order_count') ? parseInt(window.cookies.get('bezantrakta_order_count')) : 0;
        window.order['total'] = window.cookies.get('bezantrakta_order_total') ? get_price(window.cookies.get('bezantrakta_order_total')) : 0;
    }

    order_cookies_update(
        ['ticket_service_id', 'event_uuid', 'event_id', 'order_uuid', 'order_tickets', 'order_count', 'order_total']
    );
}

{# Сохранение или обновление cookies для заказа билетов #}
function order_cookies_update(cookies_list) {
    {% if debug %}console.log('order_cookies_update...');{% endif %}
    var cookie_prefix = 'bezantrakta_';
    var order_cookies = {
        // 'ticket_service_id':   window.ticket_service_id,

        'event_uuid':          window.event_uuid,
        'event_id':            window.event_id,

        'order_uuid':          window.order['uuid'],
        'order_count':         window.order['count'],
        'order_total':         window.order['total'],
        'order_tickets':       window.order['tickets'],

        'customer_order_type': window.customer['order_type'],
        'customer_name':       window.customer['name'],
        'customer_phone':      window.customer['phone'],
        'customer_email':      window.customer['email'],
        'customer_address':    window.customer['address']
    }

    for (var input = 0; input < cookies_list.length; input++) {
        for (var cookie in order_cookies) {
            if (cookies_list[input] === cookie) {
                var cookie_title = cookie;
                var cookie_value = order_cookies[cookie];

                var cookie_options = {};
                cookie_options['domain'] = '.{{ request.root_domain }}';
                {# cookies, относящиеся к покупателю, сохраняются на будущее и НЕ являются сессионными #}
                if (cookie.startsWith('customer_')) {
                    cookie_options['expires'] = new Date(new Date().getTime() + 60 * 60 * 24 * 366 * 1000);
                }

                window.cookies.set(cookie_prefix + cookie, cookie_value, cookie_options);
                {% if debug %}console.log('cookie `' + cookie_title + '`:\n', cookie_value);{% endif %}
            }
        }
    }
}

{# Обновление HTML-описания корзины заказа #}
{# Добавленные в предварительный резерв билеты выводятся в легенде страницы и отмечаются выделенными на схеме зала. #}
{# В противном случае легенда сбрасывается в состояние по умолчанию "пока ничего не выбрано". #}
function html_basket_update() {
    if (window.order['count'] > 0) {
        $('#tickets-count').html(window.order['count']);
        $('#total').html(window.order['total']);
        {% if active == 'step2' %}
            var type     = window.customer['order_type'];
            var delivery = window.customer['delivery'];
            var payment  = window.customer['payment'];
            var total    = window.order['total'];
            var extra    = window.order['extra'][type];
            {% if debug %}console.log('extra: ', extra);{% endif %}

            var courier_price = window.order['courier_price'];
            var commission    = window.order['commission'];

            overall_header = extra > 0 ? 'Всего с учётом сервисного сбора' : 'Общая сумма заказа';

            if (delivery == 'courier') {
                if (courier_price > 0) {
                    overall_header = extra > 0 ? 'Всего с учётом доставки курьером и сервисного сбора' : 'Всего с учётом доставки курьером';
                }
            }
            if (payment == 'online') {
                if (commission > 0) {
                    overall_header = extra > 0 ? 'Всего с учётом комиссии платёжной системы и сервисного сбора' : 'Всего с учётом комиссии платёжной системы';
                } else {
                    overall_header = extra > 0 ? 'Всего с учётом комиссии платёжной системы и сервисного сбора' : 'Общая сумма заказа';
                }
            }

            $('#overall-header').html(overall_header);
            {% if debug %}console.log('overall_header: ', overall_header);{% endif %}

            {# Вывод общей суммы заказа в зависимости от возможных наценок/скидок для выбранного типа заказа #}
            $('#overall').html(window.order['overall']);

            if (overall_header !== 'Общая сумма заказа') {
                $('#overall-block').show();
            } else {
                $('#overall-block').hide();
            }
        {% endif %}

        $('#no-tickets, #no-total, #buy-tickets-inactive').hide();
        $('#total-text, #buy-tickets').show();
    } else {
        $('#no-tickets, #no-total, #buy-tickets-inactive').show();
        $('#total-text, #buy-tickets').hide();
    }
}

{# Получение цены как float с двумя знаками после запятой #}
function get_price(price, commission) {
    {# Если комиссия НЕ задана - получаем цену price #}
    if (commission === undefined) {
        return Math.round(parseFloat(price) * 100) / 100;
    {# Если комиссия задана - получаем цену price с учётом commission #}
    } else if (typeof(commission) === 'number') {
        return Math.round(parseFloat(price + ((price * commission) / 100)) * 100) / 100;
    }
}

{# Получение общей суммы заказа в зависимости от возможных наценок/скидок для выбранного типа заказа #}
function get_overall() {
    var type     = window.customer['order_type'];
    var delivery = window.customer['delivery'];
    var payment  = window.customer['payment'];
    var total    = window.order['total'];
    var extra    = window.order['extra'][type];

    var courier_price = window.order['courier_price'];
    var commission    = window.order['commission'];

    {# Получение общей суммы заказа #}
    {# Для любого типа заказа - с учётом сервисного сбора для каждого билета в заказе (если он задан) #}
    var overall = total;
    if (extra > 0) {
        for (var t = 0; t < window.order['tickets'].length; t++) {
            var extra_increment = ((window.order['tickets'][t]['price'] * extra) / 100);
            overall += extra_increment;
            {% if debug %}console.log('  extra_increment: ', extra_increment);{% endif %}
        };
    }

    {% if debug %}console.log('overall_with_extra: ', overall);{% endif %}

    {# При доставке курьером - с учётом стоимости доставки курьером (если она задана) #}
    if (delivery == 'courier') {
        {% if debug %}console.log('courier_price: ', courier_price);{% endif %}
        overall += courier_price;
    }

    {# При онлайн-оплате - с учётом комиссии сервиса онлайн-оплаты (если она задана) #}
    if (payment == 'online') {
        {% if debug %}console.log('commission: ', commission);{% endif %}
        overall = get_price(overall, commission);
    }

    window.order['overall'] = overall;
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