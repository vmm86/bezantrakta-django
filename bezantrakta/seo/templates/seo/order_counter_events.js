function eventYandex() {
    yaCounter{{ request.domain_settings.counter.yandex }}.reachGoal('{{ active }}');
    console.log('eventYandex');
    return true;
}

function eventGoogle() {
    ga('send', 'event', {eventCategory: 'order', eventAction: '{{ active }}'});
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

window.order_counter_events_trigger = null;

{% if   active == 'step1' %}
    order_counter_events_trigger = document.getElementById('buy-tickets');
    if (order_counter_events_trigger) {
        order_counter_events_trigger.addEventListener('click', eventsYandexGoogle);
    }
{% elif active == 'step2' %}
    order_counter_events_trigger = document.getElementById('checkout-form');
    if (order_counter_events_trigger) {
        order_counter_events_trigger.addEventListener('submit', eventsYandexGoogle);
    }
{% elif active == 'step3' %}
window.onload = function(){
    order_counter_events_trigger = document.getElementById('success-message');
    if (order_counter_events_trigger) {
        eventsYandexGoogle();
    }
}
{% endif %}