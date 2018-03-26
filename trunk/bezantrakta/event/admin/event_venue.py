from django.contrib import admin
from django.utils.translation import ugettext as _

from project.decorators import queryset_filter

from third_party.ticket_service.models import TicketServiceSchemeVenueBinder

from ..models import EventVenue


class TicketServiceSchemeVenueBinderInline(admin.TabularInline):
    model = TicketServiceSchemeVenueBinder
    extra = 0
    fields = ('ticket_service_scheme_title', 'ticket_service_scheme_id', 'event_venue', 'ticket_service',)
    readonly_fields = ('ticket_service_scheme_title', 'ticket_service_scheme_id', 'event_venue', 'ticket_service',)
    show_change_link = True
    template = 'admin/tabular_custom.html'

    def has_add_permission(self, request):
        """
        Схемы импортируются непосредственно из сервисов продажи билетов,
        поэтому здесь они выводятся без возможности добавления.
        """
        return False


@admin.register(EventVenue)
class EventVenueAdmin(admin.ModelAdmin):
    inlines = (TicketServiceSchemeVenueBinderInline,)
    list_display = ('title', 'slug', 'ts_schemes_count', 'city',)
    list_select_related = ('city',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
    search_fields = ('title', 'slug',)

    @queryset_filter('City', 'city__slug')
    def get_queryset(self, request):
        """Фильтрация по выбранному городу."""
        return super(EventVenueAdmin, self).get_queryset(request)

    def ts_schemes_count(self, obj):
        """Количество схем залов, привязанных к конкретному залу."""
        return obj.ticketserviceschemevenuebinder_set.count()
    ts_schemes_count.short_description = _('eventvenue_ts_schemes_count')
