{# Периодическое получение списка доступных для продажи билетов и списка цен на билеты в событии #}
function ajax_seats_and_prices() {
    {% if debug %}
        console.log('ajax_seats_and_prices: ', window.seats_and_prices_id);
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

{# Фильтрация из вновь полученного списка только тех мест, состояние которых изменилось (выбраны или освобождены). #}
function ajax_seats_and_prices_success(response, status, xhr) {
    if (response) {
        {# Получение списка цен для вывода в html_basket #}
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
                prices_update('less', prices_diff);
            {# 2. Число цен увеличилось #}
            {# Добавляем актуальные цены #}
            } else if (prices_prev_size < prices_next_size) {
                var prices_diff = _.differenceWith(prices_next, prices_prev, _.isEqual);
                prices_update('more', prices_diff);
            }

            {# Обновление кэша списка цен в памяти #}
            window.prices_cache = prices_next;
            {% if debug %}console.log('prices_cache set');{% endif %}
        }

        {# Получение списка мест, свободных для заказа #}
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

            var seats_prev_keys = _.differenceWith(_.keys(seats_prev), _.keys(seats_next), _.isEqual);
            var seats_next_keys = _.differenceWith(_.keys(seats_next), _.keys(seats_prev), _.isEqual);

            {# 1. Число мест осталось прежним, но какие-то места отличаются #}
            {# Выбранные другими места - отключаем, освободившиеся места - включаем #}
            if (seats_prev_size === seats_next_size) {
                var seats_prev_diff = _.pick(seats_prev, seats_prev_keys);
                seats_update('less', seats_prev_diff);
                var seats_next_diff = _.pick(seats_next, seats_next_keys);
                seats_update('more', seats_next_diff);
            {# 2. Число мест уменьшилось #}
            {# Выбранные другими места - отключаем #}
            } else if (seats_prev_size > seats_next_size) {
                var seats_diff = _.pick(seats_prev, seats_prev_keys);
                seats_update('less', seats_diff);
            {# 3. Число мест увеличилось #}
            {# Освободившиеся места - включаем #}
            } else if (seats_prev_size < seats_next_size) {
                var seats_diff = _.pick(seats_next, seats_next_keys);
                seats_update('more', seats_diff);
            }

            {# Обновление кэша свободных мест в памяти #}
            window.seats_cache = seats_next;
            {% if debug %}console.log('seats_cache set');{% endif %}
        }

        {# Прелоадер с прогресс-баром #}
        if (_.isEmpty(seats_prev)) {
            $('#tickets-preloader').delay(1000).fadeOut(500);
        }

    } else {
        console.log('Error: ', response);
    }
}

{# Очищение свободных мест на схеме зала при ошибке запроса `ts_seats` #}
function ajax_seats_and_prices_error(xhr, status, error) {
    console.log(
        'ajax_seats_and_prices_error!', '\n',
        'xhr',    xhr,    '\n',
        'status', status, '\n',
        'error',  error
    );

    {# Обнулить кэш запрошенных ранее свободных мест #}
    window.seats_cache = [];

    {# Деактивировать все свободные и выбранные места на схеме зала #}
    $('.seat.free').removeClass('free');
    $('.seat.selected').removeClass('selected');
}

{# Обновление только отличающихся цен в html_basket #}
function prices_update(diff_state, diff) {
    {% if debug %}
    console.log('prices_diff_state: ',  diff_state);
    console.log('prices_diff_size: ', _.size(diff));
    console.log('prices_diff: ', diff);
    {% endif %}
    for (var p = 1; p < diff.length + 1; p++) {
        {# Если цен пришло больше, чем раньше - добавляем новые цены #}
        if (diff_state == 'more') {
            $('#legend-extension').append(
                '<li id="price-' + p + '">' +
                    '<span class="box color' + p + '"></span> ' + (diff[p - 1] * 1) + ' ' +
                    '<img class="ruble-sign" src="/static/global/ico/ruble_sign.svg">&nbsp;' +
                '</li>'
            );
        {# Если цен пришло меньше, чем раньше - удаляем старые цены #}
        } else if (diff_state == 'less') {
            $('#legend-extension #price-' + p).remove();
        }
    }
}

{# Обновление только отличающихся мест на схеме зала или отдельных секторов #}
function seats_update(diff_state, diff) {
    for (s in diff) {
        var ticket_id = s;
        seat = diff[s];

        var seat_selector = '.seat[data-ticket-id="' + ticket_id + '"]';

        seat['is_fixed'] = $(seat_selector).data('fixed');
        if (typeof seat['is_fixed'] === undefined) {
            seat['is_fixed'] = false;
        }

        // var class_f = 'free';
        // var class_s = 'selected';

        var is_fixed_seat = seat['is_fixed'] || seat['sector_id'] != 0;

        var ticket_title = is_fixed_seat ? (
                       seat['sector_title'] + ',\n' +
            'ряд '   + seat['row_id']       + ',\n' +
            'место ' + seat['seat_title']   + ',\n' +
            'цена '  + seat['price'] * 1
        ) : (
                       seat['sector_title'] + ',\n' +
            'цена '  + seat['price'] * 1
        );

        {# Если мест пришло больше, чем раньше - включаем освободившиеся места #}
        if (diff_state == 'more') {
            $(seat_selector).attr('data-sector-id',      seat['sector_id']);
            $(seat_selector).attr('data-sector-title',   seat['sector_title']);
            $(seat_selector).attr('data-row-id',         seat['row_id']);
            $(seat_selector).attr('data-seat-id',        seat['seat_id']);
            $(seat_selector).attr('data-seat-title',     seat['seat_title']);
            $(seat_selector).attr('data-price',          seat['price']);
            $(seat_selector).attr('data-price-order',    seat['price_order']);

            $(seat_selector).attr('title', ticket_title + ' ₽');

            $(seat_selector).addClass(window.seat_status.free.class);

            {% if ticket_service.hide_sold_non_fixed_seats %}
                $(seat_selector).show();
            {% endif %}
        {# Если мест пришло меньше, чем раньше - отключаем занятые места #}
        } else if (diff_state == 'less') {
            $(seat_selector).removeAttr('title');

            $(seat_selector).removeClass(window.seat_status.free.class);
        }
    }

    {% if ticket_service.hide_sold_non_fixed_seats %}
        {# Оставить только актуальные кликабельные билеты без мест, если они выводятся в маркированных списках #}
        if ('.non-fixed-seats .seat:not(.free, .selected)'.length) {
            $('.non-fixed-seats .seat:not(.free, .selected)').hide();
        }
    {% endif %}
}
