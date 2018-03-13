function order_cookies_get(cookie) {
    var cookie_prefix = 'bezantrakta_';
    var order_cookies = [
        'event_uuid',
        'order_uuid',

        'customer_name',
        'customer_phone',
        'customer_email',
        'customer_address',
        'customer_order_type',
    ]

    var cookie_title = order_cookies.indexOf(cookie) > -1 ? cookie_prefix + cookie : cookie;

    return Cookies.get(cookie_title);
}

function order_cookies_update(cookies_list) {
    var cookie_prefix = 'bezantrakta_';
    var order_cookies = {
        'event_uuid':          window.event_uuid,
        'order_uuid':          window.order['order_uuid'],

        'customer_name':       window.order.customer['name'],
        'customer_phone':      window.order.customer['phone'],
        'customer_email':      window.order.customer['email'],
        'customer_address':    window.order.customer['address'],
        'customer_order_type': window.order.customer['order_type']
    }

    for (var c = 0; c < cookies_list.length; c++) {
        for (var cookie in order_cookies) {
            if (cookies_list[c] === cookie) {
                var cookie_title = cookie_prefix + cookie;
                var cookie_value = order_cookies[cookie];
                var cookie_options = {};
                cookie_options['domain'] = '.{{ request.root_domain }}';
                cookie_options['expires'] = new Date(new Date().getTime() + 60 * 60 * 24 * 366 * 1000);

                Cookies.set(cookie_title, cookie_value, cookie_options);
                {% if watcher %}console.log('updated 🍪 ' + cookie + ': ', cookie_value);{% endif %}
            }
        }
    }
}

function order_cookies_delete(cookies_list) {
    var cookie_prefix = 'bezantrakta_';
    var cookie_options = {};
    cookie_options['domain'] = '.{{ request.root_domain }}';

    for (var c = 0; c < cookies_list.length; c++) {
        var cookie_title = cookie_prefix + cookies_list[c];
        var cookie_value = Cookies.get(cookie_title);

        if (cookie_value !== undefined) {
            Cookies.remove(cookie_title, cookie_options);
        }
    }
}
