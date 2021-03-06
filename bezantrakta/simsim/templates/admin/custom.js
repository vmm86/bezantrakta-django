{% load i18n %}
$(document).ready(function() {
    {# Блоки, которые должны иметь sticky-позиционирование в админ-панели #}
    sticky_blocks = [
        $('#changelist-filter'), {# Фильтры #}
        $('.submit-row')         {# Кнопки для сохранения/удаления в форме редактирования #}
    ]

    {# * фиксированное позиционирование каждого из ``sticky_blocks`` при прокручивании вниз #}
    {# * статическое позиционирование каждого из ``sticky_blocks`` при прокручивании вверх к началу страницы #}
    $.each(sticky_blocks, function(index, block) {
        if (block.length) {
            var waypoint = new Waypoint({
                element: block[0],
                handler: function(direction) {
                    if (direction == 'down') {
                        block.css('position', 'fixed');
                        $('#content').css('padding-bottom', block.height() * 1.5);
                        $('.submit-row').css('border-top', '2px solid #999');
                        $('.submit-row').css('padding', '20px 40px');
                    } else if (direction == 'up') {
                        block.css('position', 'static');
                        $('#content').css('padding-bottom', block.height() / 1.5);
                        $('.submit-row').css('border-top', 'none');
                        $('.submit-row').css('padding', '20px 12px');
                    }
                }
            });
        }
    });

    {# Сохранение данных выбранного для фильтрации сайта в cookie #}
    $('#choose_domain_or_city').change(function() {
        var selected = $('#choose_domain_or_city option:selected');
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
        {# Обновление страницы с отбрасыванием query string #}
        location.replace(window.location.href.split("?")[0]);
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
    }, 7000);

    {# Подписи к фильтру по дате #}
    if ($('input[name$="datetime__gte"]').length || $('input[name$="datetime__lte"]').length) {
        $('input[name$="datetime__gte"]').attr('placeholder', 'С');
        $('input[name$="datetime__lte"]').attr('placeholder', 'По');
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

    {# Поле для ввода произвольной причины возврата активно только при выборе этой опции #}
    if ($('.reason_choices').length) {
        $.each($('input[name="reason"]'), function(type) {
            $(this).change(function(){
                if ($('#reason_other').is(':checked')) {
                    console.log('checked');
                    $('input[name="reason_other"]').prop('disabled', false);
                } else {
                    console.log('unchecked');
                    $('input[name="reason_other"]').prop('disabled', true);
                }
            });
        });

        $('#reason_self').trigger('change');
    }
});
