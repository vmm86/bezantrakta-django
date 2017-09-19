{% spaceless %}
$(document).ready(function(){
    window.domain = '.{{ request.root_domain }}';

    Cookies.remove('bezantrakta_event_uuid',    {domain: window.domain});
    Cookies.remove('bezantrakta_event_id',      {domain: window.domain});
    Cookies.remove('bezantrakta_order_uuid',    {domain: window.domain});
    Cookies.remove('bezantrakta_order_tickets', {domain: window.domain});
    Cookies.remove('bezantrakta_order_count',   {domain: window.domain});
    Cookies.remove('bezantrakta_order_total',   {domain: window.domain});
});
{% endspaceless %}