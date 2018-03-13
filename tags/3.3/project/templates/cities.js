{# Скрытие лайтбокса для выбора городов по умолчанию #}
$('#choose-city-modal').hide();

window.http_or_https = '{{ request.http_or_https }}';
window.url_domain  = '{{ request.root_domain }}';
{# Адрес главного сайта, к которому могут добавляться поддомены #}
window.domain_slug = '{{ request.domain_slug }}'; //$('meta[name="domain"]').attr('content');
{# Получение города текущего сайта из метатега `city`, а в нём - из БД #}
window.city_slug = '{{ request.city_slug }}'; // $('meta[name="city"]').attr('content');
{# Работа с cookies #}
window.expires = new Date(new Date().getTime() + 60 * 60 * 24 * 366 * 1000);
window.domain  = '.{{ request.root_domain }}';

{# Открывать лайтбокс для выбора городов при клике на кнопку города, только если куки включены в браузере #}
$('#choose-city-button').click(function() {
    if (navigator.cookieEnabled) {
        $('body').css({'overflow': 'hidden'});
        $('#choose-city-modal').fadeIn();
    }
});

{# Создавать куку `bezantrakta_city` при клике по городу в лайтбоксе #}
$('#choose-city-list').on('click', 'li.ready', function() {
    $('body').css({'overflow': 'visible'});
    set_city($(this).data('city'));
});

{# Только если заходим куда угодно, кроме страниц событий #}
if (window.location.href.indexOf('afisha') === -1) {
    {# Удаление старой куки `city` (лучше использовать более специфичное название `bezantrakta_city`) #}
    if (Cookies.get('city')) {
        bezantrakta_city_old = Cookies.get('city');
        Cookies.remove('city', {domain: window.domain});
        set_city(bezantrakta_city_old);
    }
    {# Если кука уже создана ранее #}
    if (Cookies.get('bezantrakta_city')) {
        bezantrakta_city = Cookies.get('bezantrakta_city');
        {# Если город в куке НЕ совпадает с городом текущего сайта - редирект #}
        if (bezantrakta_city != window.city_slug) {
            redirect_city(bezantrakta_city);
        }
        {# Если город в куке совпадает с городом текущего сайта - редирект не происходит #}
        {# Это позволяет открывать несколько поддоменов в одном городе без ненужных редиректов между ними #}
    {# Если кука ещё НЕ создана #}
    } else {
        {# Вызов лайтбокса для выбора города и сохранение его в куки #}
        if (navigator.cookieEnabled) {
            $('#choose-city-modal').fadeIn();
        }
    }
}

{# Функция для создания куки `bezantrakta_city` и последующего редиректа #}
function set_city(city) {
    Cookies.set('bezantrakta_city', city, {expires: window.expires, domain: window.domain});
    redirect_city(city);
}

{# Редирект на сайт выбранного города #}
function redirect_city(city) {
    {# Если Воронеж - редирект на главный сайт, если другие города - редирект на их поддомены #}
    subdomain = city == 'vrn' ? '' : city + '.';
    window.location.href = window.http_or_https + subdomain + window.url_domain + location.pathname + location.search;
}
