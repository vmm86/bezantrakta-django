// Скрытие лайтбокса для выбора городов по умолчанию
$('#choose-city-modal').hide();

// Переменные

//// Адрес главного сайта, к которому могут добавляться поддомены
var domain = $('meta[name="domain"]').attr('content');
//// Получение города текущего сайта из метатега city_config, а в нём - из конфига Joomla
var city = $('meta[name="city"]').attr('content');

// Функции

//// Функция для получения любой куки по имени
function getCookie(name) {
  var matches = document.cookie.match(new RegExp(
    '(?:^|; )' + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)'
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}
//// Функция для создания куки `bezantrakta_city`
function setCity(city) {
    // Запись куки и редирект
    cookie_city    = 'bezantrakta_city='    + city + '; ';
    cookie_domain  = 'domain=.' + domain + '; ';
    // Период действия куки (год)
    date = new Date(new Date().getTime() + 31622400000);
    cookie_expires = 'expires=' + date.toUTCString();
    cookie = cookie_city + cookie_domain + cookie_expires;
    document.cookie = cookie;
    // Если Воронеж       - редирект на главный сайт
    // Если другие города - редирект на их поддомены
    city = city == 'vrn' ? '' : city + '.';
    window.location.href = 'http://' + city + domain + location.pathname + location.search;
}

// События

//// Открывать лайтбокс для выбора городов при клике на кнопку города,
//// только если куки включены в браузере
$('#choose-city-button').click(function() {
    if (navigator.cookieEnabled) {
        $('#choose-city-modal').fadeIn();
    }
});
// Закрывать лайтбокс для выбора городов при клике на кнопку "Закрыть"
$('#choose-city-modal .close').click(function() {
    $('#choose-city-modal').fadeOut();
});
//// Создавать куку `bezantrakta_city` при клике по городу в лайтбоксе
$('#choose-city-list').on('click', 'li.ready', function() {
    setCity($(this).data('city'));
});

// Логика работы выбора городов

// Только если заходим куда угодно, кроме страниц событий
if (window.location.href.indexOf('afisha') === -1) {
    // Удаление куки `city` (лучше использовать более специфичное название `bezantrakta_city`)
    if (getCookie('city')) {
        document.cookie = 'city=; domain=.' + domain + '; expires=Thu, 01 Jan 1970 00:00:00 GMT;';
    }
    // Если кука уже создана ранее
    if (getCookie('bezantrakta_city')) {
        // Если город в куке не совпадает с городом текущего сайта - редирект
        if (getCookie('bezantrakta_city') != city) {
            // Если Воронеж       - редирект на главный сайт
            // Если другие города - редирект на их поддомены
            city = getCookie('bezantrakta_city') == 'vrn' ? '' : getCookie('bezantrakta_city') + '.';
            window.location.href = 'http://' + city + domain + location.pathname + location.search;
        }
        // Если город в куке совпадает с городом текущего сайта - редирект не происходит
        // Это позволяет открывать несколько поддоменов в одном городе без ненужных редиректов между ними
    // Если кука ещё не создана
    } else {
        // Вызов лайтбокса для выбора города и сохранение его в куки
        if (navigator.cookieEnabled) {
            $('#choose-city-modal').fadeIn();
        }
    }
}
