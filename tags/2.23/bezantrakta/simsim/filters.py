from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter, RelatedOnlyFieldListFilter
)


class AllValuesFieldDropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class ChoicesFieldDropdownFilter(ChoicesFieldListFilter):
    template = 'admin/dropdown_filter.html'


class RelatedFieldDropdownFilter(RelatedFieldListFilter):
    template = 'admin/dropdown_filter.html'


class RelatedOnlyFieldDropdownFilter(RelatedOnlyFieldListFilter):
    template = 'admin/dropdown_filter.html'
