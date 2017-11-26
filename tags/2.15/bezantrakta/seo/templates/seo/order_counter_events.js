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

{% if   active == 'step1' %}
    document.getElementById('buy-tickets').addEventListener('click', eventsYandexGoogle);
{% elif active == 'step2' %}
    document.getElementById('checkout-form').addEventListener('submit', eventsYandexGoogle);
{% elif active == 'step3' %}
window.onload = function(){
    if (document.getElementById('success-message')) {
        eventsYandexGoogle();
    }
}
{% endif %}