from django.contrib import admin
from django.utils.translation import ugettext as _

from project.decorators import queryset_filter
from third_party.ticket_service.models import TicketServiceVenueBinder
from ..models import EventVenue


class TicketServiceVenueBinderInline(admin.TabularInline):
    model = TicketServiceVenueBinder
    extra = 0
    fields = ('ticket_service', 'ticket_service_event_venue_id', 'ticket_service_event_venue_title', 'event_venue',)
    readonly_fields = ('ticket_service', 'ticket_service_event_venue_id', 'ticket_service_event_venue_title',)

    # @queryset_filter('Domain', 'ticket_service__ticketservicedomainbinder__domain__slug')
    # def get_queryset(self, request):
    #     return super(TicketServiceVenueBinderInline, self).get_queryset(request)

    def has_add_permission(self, request):
        return False


@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    inlines = (TicketServiceVenueBinderInline,)
    list_display = ('title', 'slug', 'ts_venue_count', 'city',)
    list_select_related = ('city',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }

    @queryset_filter('City', 'city__slug')
    def get_queryset(self, request):
        return super(EventVenueAdmin, self).get_queryset(request)

    def ts_venue_count(self, obj):
        return obj.ticketservicevenuebinder_set.count()
    ts_venue_count.short_description = _('eventvenue_ts_venue_count')
