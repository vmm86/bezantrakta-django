{% spaceless %}
$(document).ready(function(){
    window.domain = '.{{ request.root_domain }}';

    Cookies.remove('bezantrakta_event_uuid',    {domain: window.domain});
    Cookies.remove('bezantrakta_event_id',      {domain: window.domain});
    Cookies.remove('bezantrakta_order_uuid',    {domain: window.domain});
    Cookies.remove('bezantrakta_order_tickets', {domain: window.domain});
    Cookies.remove('bezantrakta_order_count',   {domain: window.domain});
    Cookies.remove('bezantrakta_order_total',   {domain: window.domain});

    {# Отправка событий для отслеживания заказов в Яндекс.Метрика и Google.Analytics #}
    function eventYandex() {
        yaCounter{{ request.domain_settings.counter.yandex }}.reachGoal('step3');
        console.log('eventYandex');
        return true;
    }

    function eventGoogle() {
        ga('send', 'event', {eventCategory: 'order', eventAction: 'step3'});
        console.log('eventGoogle');
    }

    function eventsYandexGoogle() {
        try {
            eventYandex();
            eventGoogle();
        } catch(e) {
            console.log(e);
        }
    }

    window.onload = function(){
        if (document.getElementById('success-message')) {
            eventsYandexGoogle();
        }
    }
});
{% endspaceless %}