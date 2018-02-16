{# Добавление или удаление места в предварительном резерве #}
function ajax_order_reserve(ticket_id, action) {
    $.ajax({
        url: '/api/order/reserve/',
        type: 'POST',
        data: {
            'event_uuid': window.event_uuid,
            'order_uuid': window.order['order_uuid'],
            'ticket_id':  ticket_id,
            'action':     action,

            'csrfmiddlewaretoken': order_cookies_get('csrftoken')
        },
        success: ajax_order_reserve_success,
        error:   ajax_order_reserve_error
    });
}

function ajax_order_reserve_success(response, status, xhr) {
    {% if watcher %}
    console.log('reserve is_successful: ', response['success']);
    {% endif %}

    {# Если операция завершилась успешно #}
    if (response['success'] === true) {
        var ticket_id = response['ticket_id'];
        var action = response['action'];

        {% if watcher %}
        console.log('ticket_id: ', ticket_id);
        console.log('action: ', action);
        {% endif %}

        var seat_selector = '.seat[data-ticket-id="' + ticket_id + '"]';

        {# Обновление предварительного резерва #}
        window.order['tickets'] = response['tickets']
        window.order['tickets_count'] = response['tickets_count']
        window.order['total'] = response['total']

        {% if watcher %}
        console.log(
            'order_tickets: ', window.order['tickets'],       '\n',
            'order_count: ',   window.order['tickets_count'], '\n',
            'order_total: ',   window.order['total']
        );
        {% endif %}

        if (action == window.seat_status.free.action) {
            $(seat_selector).addClass(window.seat_status.selected.class);
            $(seat_selector).removeClass(window.seat_status.free.class);
        } else if (action == window.seat_status.selected.action) {
            $(seat_selector).addClass(window.seat_status.free.class);
            $(seat_selector).removeClass(window.seat_status.selected.class);
        }

        html_basket_update();
    }
    {# Если добавление или удаление места завершилось НЕуспешно - ничего не происходит #}

    {% if active == 'step1' %}
        {# Прелоадер с прогресс-баром #}
        $('#tickets-preloader').delay(1000).fadeOut(25);
    {% elif active == 'step2' %}
        {# Включение возможности подтвердить заказ после удаления очередного билета, если заказ ещё не пустой #}
        var no_tickets = _.isEmpty(window.order['tickets']);
        if (no_tickets === false && window.order_timeout > 10000) {
            $('#agree, #isubmit').prop('disabled', false);
            $('#back').show();
            $('#back-inactive').hide();
        }
    {% endif %}
}

function ajax_order_reserve_error(xhr, status, error) {
    console.log(
        'ajax_order_reserve_error!', '\n',
        'xhr',    xhr,    '\n',
        'status', status, '\n',
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
            $('#back').show();
            $('#back-inactive').hide();
        }
    {% endif %}
}
