{# Точка входа для работы с заказами #}
function welcome() {
    {# Прелоадер с прогресс-баром #}
    $('#tickets-preloader').show();

    {# Удаление устаревших более не нужных cookies #}
    order_cookies_delete(['ticket_service_id', 'event_id', 'order_tickets', 'order_count', 'order_total']);

    window.event_uuid = '{{ event.event_uuid }}';

    var order_uuid = order_cookies_get('order_uuid');
    window.order_uuid = order_uuid ? order_uuid : 'None';

    {# Попытка удалить старый предварительный резерв из другого события, если он был сделан ранее #}
    ajax_order_prev_order_delete();
    {# Получение информации о предварительном резерве #}
    ajax_order_initialize();
}

{# Инициализация проверок по таймаутам при загрузке страницы #}
function start_heartbeat() {
    window.seat_status = {
        free:     {class: 'free',     action: 'add'},
        selected: {class: 'selected', action: 'remove'}
    }

    {# Периодические проверки состояния мест с обратным отсчётом до их освобождения #}
    window.countdown_id = setInterval(seat_countdown_timer, 1000);
    {% if watcher %}console.log('started countdown ' + window.countdown_id);{% endif %}

    {% if active == 'step1' %}
        {# Кэш запрошенных ранее списка цен и свободных мест для сравнения с вновь пришедшими свободными местами #}
        window.prices_cache = [];
        window.seats_cache  = [];

        {# Первый запрос свободных для продажи мест при загрузке страницы #}
        ajax_seats_and_prices();

        {# Периодические запросы списка цен и свободных для продажи мест в событии #}
        window.seats_and_prices_id = setInterval(ajax_seats_and_prices, window.heartbeat_timeout * 1000);
        {% if watcher %}console.log('started heartbeat ' + window.seats_and_prices_id);{% endif %}

        {# Добавлять и убирать в предварительном резерве можно только доступные к заказу места #}
        $('#tickets').on('click', '.seat.free, .seat.selected', seat_click_handler);
        {# Селектор `#tickets` указан для того, чтобы работали клики по схемам отдельных секторов в больших залах, когда эти схемы ещё добавлялись "на лету" в jQuery #}
        {# Селектор `#tickets`, к которому применяется `.on()`, НЕ должен генерироваться уже после загрузки страницы, будучи при этом родителем для вновь генерируемых элементов #}

        {# Отключение запроса мест при переходе на шаг 2, #}
        {# чтобы очередной запуск `ajax_seats_and_prices` не мог бы завершился с ошибкой #}
        $('#buy-tickets').on('click', stop_heartbeat);
    {% elif active == 'step2' %}
        {# Текущий средний совокупный таймаут всех билетов в предварительном резерве, #}
        {# по истечении которого блокируется подтверждение заказа на шаге 2 #}
        window.order_timeout = window.seat_timeout * 60 * 1000;
        {% if watcher %}console.log('order_timeout (initial): ', window.order_timeout);{% endif %}

        {# Отключение проверки состояния мест при уходе назад на шаг 1 или при подтверждении заказа #}
        $('#back').on('click', stop_heartbeat);
        $('#checkout-form').on('submit', stop_heartbeat);
    {% endif %}

    return true;
}

{# Остановка проверок по таймаутам при достижении определённых условий #}
function stop_heartbeat() {
    {% if active == 'step1' %}
        clearInterval(window.seats_and_prices_id);
        {% if watcher %}console.log('stopped seats_and_prices ' + window.seats_and_prices_id);{% endif %}
        $('#tickets-preloader').show();
    {% endif %}

    clearInterval(window.countdown_id);
    {% if watcher %}console.log('stopped countdown ' + window.countdown_id);{% endif %}
}

function order_after_initialize() {
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
        {# Заполение реквизитов покупателя из cookies, если они вводились им ранее #}
        for (property in window.order.customer) {
            var customer_input = '#customer-' + property;
            if (window.order.customer[property] != null) {
                $(customer_input).val(window.order.customer[property]);
            } else {
                if (property == 'address') {
                    $(customer_input).val('{{ domain.city_title }}');
                }
            }
        };

        {# При начальной загрузке страницы скрытие всех блоков, появляющихся при выборе чекбоксов #}
        $('#overall-block, .ticket-offices-contacts, .customer-address, .payment-info, .eticket-info').hide();

        {# Логика переключения чекбоксов при выборе способа заказа #}
        window.order_types = {
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

        $.each(window.order_types, function(type) {
            $(window.order_types[type]['field']).change(function(){
                ajax_order_change_type(type);
            });
        });

        {# Выбор ккого-то типа заказа билетов по умолчанию, активного в данном событии #}
        $('input[name="customer_order_type"][class="{{ default_order_type }}"').prop('checked', true);
        $('input[name="customer_order_type"][class="{{ default_order_type }}"').trigger('change');

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
                window.order.customer['name'] = $(this).val();
                order_cookies_update(['customer_name']);
            });

            if ($(this).val().length > 0) {
                var type = $('input[name="customer_order_type"]:checked').val();
                ajax_order_change_type(type);
            }
        });

        {# Поле "Телефон" #}
        {# Обрезка лишних пробелов в начале и в конце #}
        $('#customer-phone').blur(function() {
            $(this).val($.trim($(this).val()));
            window.order.customer['phone'] = $(this).val();
            order_cookies_update(['customer_phone']);

            if ($(this).val().length > 0) {
                var type = $('input[name="customer_order_type"]:checked').val();
                ajax_order_change_type(type);
            }
        });

        {# Поле "Email" #}
        {# Контроль ввода правильного email-адреса, обрезка лишних пробелов в начале и в конце #}
        $('#customer-email').blur(function() {
            var test_email = /^\s*[A-Z0-9._%+-]+@([A-Z0-9-]+\.)+[A-Z]{2,4}\s*$/i;
            if (test_email.test(this.value)) {
                $(this).val($.trim($(this).val()));
                window.order.customer['email'] = $(this).val();
                order_cookies_update(['customer_email']);

                if ($(this).val().length > 0) {
                    var type = $('input[name="customer_order_type"]:checked').val();
                    ajax_order_change_type(type);
                }
            } else {
                alert('Пожалуйста, укажите правильный email-адрес');
            }
        });

        {# Поле "Адрес" #}
        {# Обрезка лишних пробелов в начале и в конце #}
        $('#customer-address').blur(function() {
            $(this).val($.trim($(this).val()));
            window.order.customer['address'] = $(this).val();
            order_cookies_update(['customer_address']);

            if ($(this).val().length > 0) {
                var type = $('input[name="customer_order_type"]:checked').val();
                ajax_order_change_type(type);
            }
        });
    {% endif %}

    {% comment %}
    {# Фиксированное позиционирование легенды заказа и кнопок "Назад"/"Оформить" при прокручивании страницы #}
    $(window).scroll(function(){
        console.log('scroll:', $(window).scrollTop());
        legend_position = $('#basket-container').position().top;
        if ($(window).scrollTop() >= legend_position) {
            $('#basket-container').css('position', 'fixed');
        } else {
            $('#basket-container').css('position', 'static');
        }
    });
    {% endcomment %}
}

{# Обработка клика на свободном месте в схеме зала #}
function seat_click_handler(click) {
    click.preventDefault();

    {# Прелоадер с прогресс-баром #}
    $('#tickets-preloader').fadeIn(20);

    var ticket_id = $(this).data('ticket-id');
    var action = undefined;

    {# Если выбираем НЕ выбранное ранее место #}
    if ($(this).hasClass(window.seat_status.free.class)) {
        action = window.seat_status.free.action;
    {# Если снимаем выделенее с ранее выбранного места #}
    } else if ($(this).hasClass(window.seat_status.selected.class)) {
        action = window.seat_status.selected.action;
    }

    ajax_order_reserve(ticket_id, action);
}

{# Обратный отсчёт до освобождения добавленных в предварительный резерв мест #}
function seat_countdown_timer() {
    var updated = new Date();
    {# Таймаут для выделения места в миллисекундах #}
    var seat_timeout_ms = window.seat_timeout * 60 * 1000;
    {% if active == 'step2' %}
    var order_timeout_ms = 0;

    {# Если все билеты удалены из предварительного резерва - перезагрузить страницу #}
    if (window.order['tickets_count'] == 0) {
        stop_heartbeat();

        html_basket_update();

        location.reload();
    }
    {% endif %}

    {# Выбранные ранее билеты: #}
    {# * ЛИБО сохраняются в заказе, если их таймаут ещё не прошёл #}
    {# * ЛИБО удаляются из корзины заказа, если их таймаут уже прошёл #}
    for (t in window.order['tickets']) {
        var ticket_id = t;
        ticket = window.order['tickets'][t];

        {# Разница между временем обновления мест и временем резерва конкретного места #}
        var added = new Date(ticket['added']);
        var updated_minus_added_ms = updated - added;

        {# Вывод обратного отсчёта до автоматического освобождения места #}
        var uma = new Date(seat_timeout_ms - updated_minus_added_ms);
        var min = uma.getMinutes();
        var sec = uma.getSeconds();
        min = min >= 0 && min < 10 ? '0' + min : min;
        sec = sec >= 0 && sec < 10 ? '0' + sec : sec;
        $('#' + ticket_id + '_countdown').html('(' + min + ':' + sec + ')');

        {# Если заданный таймаут для резерва места прошёл - место освобождается #}
        if (updated_minus_added_ms > seat_timeout_ms) {
            $('#' + ticket_id + '_countdown').html('(00:00)');

            {# При истечении таймаута на резерв ЕДИНОЖДЫ запрашиваем удаление из предварительного резерва #}
            {# Если удаление НЕ завершится из-за ошибки - место просто удалится из корзины заказа в браузере #}
            if (ticket['remove_in_progress'] !== true) {
                ticket['remove_in_progress'] = true;

                $('#' + ticket_id).remove();

                ajax_order_reserve(ticket_id, 'remove');
            }
    {% if active == 'step2' %}
        } else {
            ticket['order_timeout_ms'] = seat_timeout_ms - updated_minus_added_ms;

            {# Временное отключение возможности подтвердить заказ при удалении очередного билета из резерва #}
            if (ticket['order_timeout_ms'] < 5000) {
                $('#agree, #isubmit').prop('disabled', true);
                $('#back').hide();
                $('#back-inactive').show();
            }

            order_timeout_ms += ticket['order_timeout_ms'];
    {% endif %}
        }
    }

    {% if active == 'step2' %}
        window.order_timeout = order_timeout_ms > 0 ? parseInt(order_timeout_ms / window.order['tickets_count']) : 11000;
        {% if watcher %}console.log('window.order_timeout: ', window.order_timeout);{% endif %}

        {# Если средний совокупный таймаут всех билетов в заказе меньше 10 секунд - #}
        {# возможность подтверждения заказа отключается во избежание ошибок #}
        if (window.order_timeout < 10000) {
            $('#agree, #isubmit').prop('disabled', true);
            $('#back').hide();
            $('#back-inactive').show();
            {% if watcher %}console.log('order_timeout is coming...');{% endif %}
        }
    {% endif %}
}

{# Обновление HTML-описания корзины заказа #}
{# Добавленные в предварительный резерв билеты выводятся в легенде страницы и отмечаются выделенными на схеме зала. #}
{# В противном случае легенда сбрасывается в состояние по умолчанию "пока ничего не выбрано". #}
function html_basket_update() {
    $('#chosen-tickets').empty();

    if (window.order['tickets_count'] > 0) {
        {# Вывод билетов в предварительном резерве, отсортированных по ключам в order[tickets] #}
        var sorted_tickets_keys = _.sortBy(Object.keys(window.order['tickets']));

        for (var i = 0; i < sorted_tickets_keys.length; i++) {
            var ticket_id = sorted_tickets_keys[i];
            var ticket = window.order['tickets'][ticket_id];

            var seat_selector = '.seat[data-ticket-id="' + ticket_id + '"]';

            ticket['is_fixed'] = $(seat_selector).data('fixed');
            if (typeof ticket['is_fixed'] === undefined) {
                ticket['is_fixed'] = false;
            }

            var is_fixed_seat = ticket['is_fixed'] || ticket['sector_id'] != 0;

            var ticket_title = is_fixed_seat ? (
                           ticket['sector_title'] + ',\n' +
                'ряд '   + ticket['row_id']       + ',\n' +
                'место ' + ticket['seat_title']   + ',\n' +
                'цена '  + get_price(ticket['price'])
            ) : (
                           ticket['sector_title'] + ',\n' +
                'цена '  + get_price(ticket['price'])
            );

            var seat_timeout_output = window.seat_timeout < 10 ? '0' + window.seat_timeout : window.seat_timeout;
            $('#chosen-tickets').append(
                '<li id="'   + ticket_id + '">' +
                '<span id="' + ticket_id + '_countdown" class="countdown">(' + seat_timeout_output + ':00)</span> ' +
                ticket_title + ' <img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">' +
                '</li>'
            );

            {# Выбранные места на схеме зала отмечаются только на шаге 1 со схемой зала #}
            {% if active == 'step1' %}
                $(seat_selector).addClass(window.seat_status.selected.class);
                $(seat_selector).removeClass(window.seat_status.free.class);

                $(seat_selector).attr('data-sector-id',      ticket['sector_id']);
                $(seat_selector).attr('data-sector-title',   ticket['sector_title']);
                $(seat_selector).attr('data-row-id',         ticket['row_id']);
                $(seat_selector).attr('data-seat-title',     ticket['seat_title']);
                $(seat_selector).attr('data-price',          ticket['price']);
                $(seat_selector).attr('data-price-order',    ticket['price_order']);

                $(seat_selector).attr('title', ticket_title + ' ₽');
            {% endif %}
        }

        $('#tickets-count').html(window.order['tickets_count']);

        $('#total').html(get_price(window.order['total']));

        {% if active == 'step2' %}
            $('#overall').html(get_price(window.order['overall']));
            $('#overall-header').html(window.order['overall_header']);
            window.order['overall'] !== window.order['total'] ? $('#overall-block').show() : $('#overall-block').hide();

            {% if watcher %}
                console.log('overall_header: ', window.order['overall_header']);
                console.log('overall: ', window.order['overall']);
            {% endif %}
        {% endif %}

        $('#no-tickets, #no-total, #buy-tickets-inactive').hide();
        $('#total-text, #buy-tickets').show();
    } else {
        $('#no-tickets, #no-total, #buy-tickets-inactive').show();
        $('#total-text, #buy-tickets').hide();
    }
}

{# Показ выбранного сектора и скрытие всех НЕвыбранных секторов #}
function sectors_handler() {
    {# Скрытие каждого из секторов по умолчанию #}
    $('.sectors-slider .sectors').hide();

    sector_scheme = '.sectors-slider > .' + $(this).attr('id');
    if ($(this).is(':checked')) {
        {% if watcher %}console.log(sector_scheme, 'checked');{% endif %}
        $(sector_scheme).show();
    }
}

{# Логика переключения чекбокса о согласии на обработку персональных данных #}
function is_agree() {
    var is_agree = $('#agree').prop('checked') === true ? false : true;
    $('#isubmit').prop('disabled', is_agree);
}

{# Получение цены как float с двумя знаками после запятой #}
function get_price(price) {
    return Math.round(parseFloat(price) * 100) / 100;
}

function log_success(data, status) {
    console.log('Success!', '\nStatus: ', status, '\nData: ', data);
}

function log_error(data, status, error) {
    console.log('Error!', '\nStatus: ', status, '\nError: ', error, '\nData: ', data.responseText);
}
