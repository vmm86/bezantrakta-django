def domain_filter(field):
    """
    Фильтрация записей модели в админке по сайту,
    если эта модель привязана к Domain по внешнему ключу domain.
    """
    def filter_queryset(get_queryset):
        def wrapper(self, request):
            queryset = get_queryset(self, request)
            domain_filter = request.COOKIES.get('bezantrakta_admin_domain', None)
            if domain_filter and domain_filter != '':
                return queryset.filter(**{field: domain_filter})
            else:
                return queryset
        return wrapper
    return filter_queryset
