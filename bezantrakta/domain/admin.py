from django.contrib import admin

# from django_admin_listfilter_dropdown.filters import DropdownFilter
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .models import Domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'is_online',)
    search_fields = ('slug', 'title',)
    list_filter = (('city', RelatedDropdownFilter),)
