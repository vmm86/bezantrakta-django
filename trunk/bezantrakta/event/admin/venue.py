from django.contrib import admin

from project.decorators import domain_filter
from ..models import EventVenue


@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'domain',)
    list_select_related = ('domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }

    @domain_filter('domain__slug')
    def get_queryset(self, request):
        return super().get_queryset(request)
