{# Выбор типа заказа из имеющихся вариантов #}
function ajax_order_change_type(order_type) {
    $.ajax({
        url: '/api/order/change_type/',
        type: 'POST',
        data: {
            'customer': JSON.stringify(window.order.customer),
            'order_uuid': window.order_uuid,
            'order_type': order_type,

            'csrfmiddlewaretoken': order_cookies_get('csrftoken')
        },
        success: ajax_change_order_type_success,
        error:   ajax_change_order_type_error
    });
}

function ajax_change_order_type_success(response, status, xhr) {
    if (response['success'] === true) {
        {# Получение обновлённого предварительного резерва #}
        window.order = response['order'];

        var order_type = window.order.customer['order_type']

        $(window.order_types[order_type]['hide']).hide();
        $(window.order_types[order_type]['show']).show();

        {# Обновить выбранный тип заказа в cookies #}
        order_cookies_update(['customer_order_type']);

        html_basket_update();

        {% if watcher %}
            console.log('order after change_type: ', window.order);
            console.log('order_type: ', order_type);
            console.log('overall: ', window.order['overall']);
            console.log('overall_header: ', window.order['overall_header']);
        {% endif %}
    }
}

function ajax_change_order_type_error(xhr, status, error) {
    console.log(
        'ajax_change_order_type error!', '\n',
        'xhr',    xhr,    '\n',
        'status', status, '\n',
        'error',  error
    );
}
