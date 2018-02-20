{# Инициализация заказа (получение параметров нового или существующего заказа) #}
function ajax_order_prev_order_delete() {
    $.ajax({
        url: '/api/order/prev_order_delete/',
        type: 'POST',
        data: {
            'event_uuid': window.event_uuid,
            'order_uuid': window.order_uuid,

            'csrfmiddlewaretoken': order_cookies_get('csrftoken')
        },
        success: ajax_order_prev_order_delete_success,
        error:   ajax_order_prev_order_delete_error
    });
}

function ajax_order_prev_order_delete_success(response, status, xhr) {
    {% if watcher %}
    console.log('prev_order_delete: ', response);
    {% endif %}
}

function ajax_order_prev_order_delete_error(xhr, status, error) {
    console.log(
        'ajax_order_prev_order_delete_error!', '\n',
        'xhr',    xhr,    '\n',
        'status', status, '\n',
        'error',  error
    );
}
