{# Инициализация заказа (получение параметров нового или существующего заказа) #}
function ajax_order_initialize() {
    $.ajax({
        url: '/api/order/initialize/',
        type: 'GET',
        data: {
            'event_uuid': window.event_uuid,
            'order_uuid': window.order_uuid
        },
        success: ajax_order_initialize_success,
        error:   ajax_order_initialize_error
    });
}

function ajax_order_initialize_success(response, status, xhr) {
    {% if debug %}
    console.log('order initialized: ', response['order']);
    {% endif %}

    {# Получение параметров предварительного резерва (нового или существующего) #}
    window.order = response['order'];

    {# Получение данных покупателя из cookies #}
    window.customer = {};
    window.customer['name']    = window.cookies.get('bezantrakta_customer_name');
    window.customer['phone']   = window.cookies.get('bezantrakta_customer_phone');
    window.customer['email']   = window.cookies.get('bezantrakta_customer_email');
    window.customer['address'] = window.cookies.get('bezantrakta_customer_address');

    order_cookies_update(
        ['event_uuid', 'order_uuid']
    );

    {# Запуск работы с предварительным резервом билетов на сайте после его получения #}
    start_heartbeat();
    order_after_initialize();
}

function ajax_order_initialize_error(xhr, status, error) {
    console.log(
        'ajax_order_initialize_error!', '\n',
        'xhr',    xhr,    '\n',
        'status', status, '\n',
        'error',  error
    );
}
