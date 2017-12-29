{% load i18n %}
$(document).ready(function() {
    {# Фиксированное позиционирование кнопок для сохранения/удаления в форме редактирования при прокручивании вниз #}
    if ($('.submit-row').length) {
        var waypoint = new Waypoint({
            element: $('.submit-row')[0],
            handler: function(direction) {
                if (direction == 'down') {
                    $('.submit-row').css('position', 'fixed');
                    $('#content').css('padding-bottom', '40px');
                } else if (direction == 'up') {
                    $('.submit-row').css('position', 'static');
                    $('#content').css('padding-bottom', '20px');
                }
            }
        });
    }

    {# Сохранение данных выбранного для фильтрации сайта в cookie #}
    $('#choose_domain').change(function() {
        var selected = $('#choose_domain option:selected');
        var domain_slug = selected.val();
        var domain_id = selected.data('domain-id');
        var city_slug = selected.data('city-slug');
        var city_id = selected.data('city-id');
        var timezone = selected.data('timezone');
        {# Адрес главного сайта, к которому могут добавляться поддомены #}
        var domain = '.{{ request.root_domain }}';
        {# Период действия куки (год) #}
        var expires = new Date(new Date().getTime() + 1000 * 60 * 60 * 24 * 366);
        {# Запись в cookie выбранного домена для фильтрации админки #}
        Cookies.set('bezantrakta_admin_domain', domain_slug, {expires: expires, domain: domain});
        Cookies.set('bezantrakta_admin_domain_id', domain_id, {expires: expires, domain: domain});
        {# Запись в cookie текущего часового пояса для локализации отображения даты/времени в админке #}
        Cookies.set('bezantrakta_admin_city', city_slug, {expires: expires, domain: domain});
        Cookies.set('bezantrakta_admin_city_id', city_id, {expires: expires, domain: domain});
        {# Запись в cookie текущего часового пояса для локализации отображения даты/времени в админке #}
        Cookies.set('bezantrakta_admin_timezone', timezone, {expires: expires, domain: domain});
        location.reload();
    });

    {# При создании новых записей #}
    var city_id = Cookies.get('bezantrakta_admin_city_id');
    var domain_id = Cookies.get('bezantrakta_admin_domain_id');
    if (domain_id !== 0) {
        $('.object-tools .addlink').attr('href', function(i, h) {
            var qs = h + (h.indexOf('?') != -1 ? '&' : '?');
            return qs + 'domain=' + domain_id + '&city=' + city_id;
        });
    }

    {# Удаление всплывающих уведомлений #}
    setTimeout(function(){
        $.each($('.messagelist li'), function(index, val) {
            $(this).remove();
        });
    }, 4000);

    {# Подписи к фильтру по дате #}
    if ($('#id_datetime__gte').length || $('#id_datetime__lte').length) {
        $('#id_datetime__gte').attr('placeholder', 'С');
        $('#id_datetime__lte').attr('placeholder', 'По');
        $('.admindatefilter input[type=\'reset\']').val('Очистить');
    }

    {# Показ процесса заполнения title, description, keywords #}
    $('#id_title + .help').prepend('<strong id="id_title_info"></strong><br>');
    $('#id_description + .help').prepend('<strong id="id_description_info"></strong><br>');
    $('#id_keywords + .help').prepend('<strong id="id_keywords_info"></strong><br>');

    $('#id_title, #id_description, #id_keywords').each(function() {
            var thisElement = '#' + this.id + '_info';
            var maxLength = $(this).attr('maxlength');
            var currentLength = $(this).val().length;
            $(this).val( $(this).val().substr(0, maxLength) );
            var remaningLength = maxLength - currentLength;
            if (remaningLength < 0) {
                remaningLength = 0;
            }
            var warnLength = $(this).attr('warnlength');
            $(thisElement).html('набрано ' + currentLength + ' симв.');
            if (remaningLength < warnLength) {
                $(this).css('background-color', '#FF7F7F');
                $(thisElement).css('color', 'red');
            } else {
                $(this).css('background-color', '#FFF');
                $(thisElement).css('color', 'black');
            }
    });
    $(function() {
        $('#id_title, #id_description, #id_keywords').keyup(function() {
            var thisElement = '#' + this.id + '_info';
            var maxLength = $(this).attr('maxlength');
            var currentLength = $(this).val().length;
            $(this).val( $(this).val().substr(0, maxLength) );
            var remaningLength = maxLength - currentLength;
            if (remaningLength < 0) {
                remaningLength = 0;
            }
            var warnLength = $(this).attr('warnlength');
            $(thisElement).html('набрано ' + currentLength + ' симв.');
            if (remaningLength < warnLength) {
                $(this).css('background-color', '#FF7F7F');
                $(thisElement).css('color', 'red');
            } else {
                $(this).css('background-color', '#FFD');
                $(thisElement).css('color', 'black');
            }
        })
    });

    {# Справка по работе с позициями афиш в конейнерах #}
    $('#eventcontainerbinder_set-group table').after('{% trans "eventcontainerbinder_order_help_text" %}');

    {# Стилизация строк в таблице заказов в зависимости от из статуса #}
    $('.model-order #result_list tbody tr').each(function(index, element) {
        status_description = $(this).children('.field-status').html();

        if (status_description === 'создан') {
            $(this).addClass('ordered');
        } else if (status_description === 'подтверждён') {
            $(this).addClass('approved');
        } else if (status_description === 'отменён') {
            $(this).addClass('cancelled');
        } else if (status_description === 'возвращён') {
            $(this).addClass('refunded');
        }

    });
});