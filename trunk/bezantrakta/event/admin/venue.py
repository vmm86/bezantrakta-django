from django.contrib import admin

from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from ..models import EventVenue


@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'domain',)
    list_filter = (
        ('domain', RelatedDropdownFilter),
    )
