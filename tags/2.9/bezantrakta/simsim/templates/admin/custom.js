{% load i18n %}
$(document).ready(function() {
    {# Сохранение данных выбранного для фильтрации сайта в cookie #}
    $('#choose_domain').change(function() {
        var value = $('#choose_domain option:selected').val();
        var city = $('#choose_domain option:selected').data('city');
        var timezone = $('#choose_domain option:selected').data('timezone');
        {# Адрес главного сайта, к которому могут добавляться поддомены #}
        var domain = '.{{ request.root_domain }}';
        {# Период действия куки (год) #}
        var expires = new Date(new Date().getTime() + 1000 * 60 * 60 * 24 * 366);
        {# Запись в cookie выбранного домена для фильтрации админки #}
        Cookies.set('bezantrakta_admin_domain', value, {expires: expires, domain: domain});
        {# Запись в cookie текущего часового пояса для локализации отображения даты/времени в админке #}
        Cookies.set('bezantrakta_admin_city', city, {expires: expires, domain: domain});
        {# Запись в cookie текущего часового пояса для локализации отображения даты/времени в админке #}
        Cookies.set('bezantrakta_admin_timezone', timezone, {expires: expires, domain: domain});
        location.reload();
    });

    {# При создании новых записей #}
    {# var city_id = {{ bezantrakta_admin_city_id }}; #}
    var domain_id = {{ bezantrakta_admin_domain_id }};
    if (domain_id !== 0) {
        $('.object-tools .addlink').attr('href', function(i, h) {
            var qs = h + (h.indexOf('?') != -1 ? '&' : '?');
            return qs + 'domain=' + domain_id; {# + '&city=' + city_id; #}
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

    {# Добавление событий в группе работает только для группы #}
    {# Добавление ссылок доступно только в событиях и в группе не работает #}
    function show_hide_add_group_link(){
        if (
            $('#id_is_group').prop('checked') === true || $('.field-is_group .readonly img').attr('alt') === 'True'
        ) {
            $('#groups-group .tabular table .add-row a').show();
            $('#eventlinkbinder_set-group .tabular table .add-row a').hide();
        } else {
            $('#groups-group .tabular table .add-row a').hide();
            $('#eventlinkbinder_set-group .tabular table .add-row a').show();
        }
    }
    show_hide_add_group_link();
    $('#id_is_group').click(function(){
        show_hide_add_group_link();
    });

    {# Справка по работе с позициями афиш в конейнерах #}
    $('#eventcontainerbinder_set-group table').after('{% trans "eventcontainerbinder_order_help_text" %}');

    {# Стилизация строк в таблице заказов в зависимости от из статуса #}
    $('.model-order #result_list tbody tr').each(function(index, element) {
        status_description = $(this).children('.field-status').html();
        console.log(index, element, status);

        if (status_description === 'создан') {
            if ($(this).hasClass('row1')) {
                $(this).css('background-color', '#c7d6e7');
            } else if ($(this).hasClass('row2')) {
                $(this).css('background-color', '#b5c9df');
            }
        } else if (status_description === 'подтверждён') {
            if ($(this).hasClass('row1')) {
                $(this).css('background-color', '#d9eeda');
            } else if ($(this).hasClass('row2')) {
                $(this).css('background-color', '#c7e7c8');
            }
        } else if (status_description === 'отменён') {
            if ($(this).hasClass('row1')) {
                $(this).css('background-color', '#e7c8c7');
            } else if ($(this).hasClass('row2')) {
                $(this).css('background-color', '#dfb7b5');
            }
        } else if (status_description === 'возвращён') {
            if ($(this).hasClass('row1')) {
                $(this).css('background-color', '#c8c7e7');
            } else if ($(this).hasClass('row2')) {
                $(this).css('background-color', '#b6b5df');
            }
        }

    });
});