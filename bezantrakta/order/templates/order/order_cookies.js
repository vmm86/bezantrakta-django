{# Модификация работы с Cookies, чтобы избежать ненужного urlendoding #}
window.cookies = Cookies.withConverter({
    read:  function (value, name) { return value; },
    write: function (value, name) { return value; }
});

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
                {# cookies, относящиеся к покупателю, сохраняются на будущее и НЕ являются сессионными #}
                if (cookie.startsWith('customer_')) {
                    cookie_options['expires'] = new Date(new Date().getTime() + 60 * 60 * 24 * 366 * 1000);
                }

                window.cookies.set(cookie_title, cookie_value, cookie_options);
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
        var cookie_value = window.cookies.get(cookie_title);

        if (cookie_value !== undefined) {
            window.cookies.remove(cookie_title, cookie_options);
        }
    }
}
