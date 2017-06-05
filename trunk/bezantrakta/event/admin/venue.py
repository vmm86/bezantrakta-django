from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from ..models import EventVenue


@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    list_display = ('title', 'domain',)
    list_filter = (
        ('domain', RelatedDropdownFilter),
    )
    list_select_related = ('domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
