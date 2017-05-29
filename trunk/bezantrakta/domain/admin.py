from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from .models import Domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_online',)  # is_published
    list_filter = (
        ('city', RelatedDropdownFilter),
    )
    search_fields = ('title', 'slug',)
