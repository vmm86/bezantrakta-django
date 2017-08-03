def queryset_filter(model_name, field_name):
    """
    Фильтрация записей в админке по специфическому полю field_name модели model_name,
    связанной с исходной моделью по соответствующему внешнему ключу.

    Args:
        model_name (str): Название модели для фильтрации по его полю
        field_name (str): Поле модели для фильтрации

    Returns:
        function: Результаты исходного запроса с фильтрацией или без
    """
    def queryset_filter_wrapper(get_queryset):
        def wrapper(self, request):
            qs = get_queryset(self, request)
            qs_filters = {
                'City':   'bezantrakta_admin_city',
                'Domain': 'bezantrakta_admin_domain',
            }
            for mod, value in qs_filters.items():
                if mod == model_name:
                    qs_filter = request.COOKIES.get(value)
                    # print('qs_filter: ', qs_filter, ' mod: ', mod, ' model_name: ', model_name)
                    break
                else:
                    qs_filter = ''
                    # print('qs_filter: empty')
            qs = qs.filter(**{field_name: qs_filter}) if qs_filter and qs_filter != '' else qs
            return qs
        return wrapper
    return queryset_filter_wrapper
