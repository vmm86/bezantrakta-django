from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from ..models import EventGroup


@admin.register(EventGroup)
class EventGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'domain',)
    list_filter = (
        ('domain', RelatedDropdownFilter),
    )
    list_select_related = ('domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
