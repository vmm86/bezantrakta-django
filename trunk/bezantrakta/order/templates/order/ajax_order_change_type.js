{# Выбор типа заказа из имеющихся вавиантов #}
function ajax_order_change_type(type) {
    $.ajax({
        url: '/api/order/change_type/',
        type: 'POST',
        data: {
            'order_type': type,

            'csrfmiddlewaretoken': window.cookies.get('csrftoken')
        },
        success: ajax_change_order_type_success,
        error:   ajax_change_order_type_error
    });
}

function ajax_change_order_type_success(response, status, xhr) {
    {# Обновить выбранный тип заказа (response == order ) #}
    window.customer['order_type'] = response['order_type'];
    order_cookies_update(['customer_order_type']);

    window.customer['delivery'] = response['delivery'];  // ???
    window.customer['payment'] = response['payment'];  // ???
    $('#delivery').val(window.customer['delivery']);  // ???
    $('#payment').val(window.customer['payment']);  // ???

    window.order['total'] = response['total'];
    window.order['overall'] = response['overall'];

    window.order['courier_price'] = response['courier_price'];  // ???
    window.order['commission'] = response['commission'];  // ???

    // get_overall();

    html_basket_update();

    {% if debug %}
        console.log('order_type: ', window.customer['order_type'], '\n',
                    'overall: ',    window.order['overall']);
    {% endif %}
}

function ajax_change_order_type_error(xhr, status, error) {
    console.log(
        'ajax_prev_order_delete_error!', '\n',
        'xhr',    xhr,    '\n',
        'status', status, '\n',
        'error',  error
    );
}
