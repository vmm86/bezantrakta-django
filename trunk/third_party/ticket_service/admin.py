from django.contrib import admin
from django.db.models import TextField
from django.utils.translation import ugettext as _

from jsoneditor.forms import JSONEditor

from project.decorators import queryset_filter
from .models import TicketService, TicketServiceVenueBinder


@admin.register(TicketServiceVenueBinder)
class TicketServiceVenueBinderAdmin(admin.ModelAdmin):
    list_display = ('ticket_service_event_venue_title', 'ticket_service_event_venue_id',
                    'if_scheme_exists', 'ticket_service',)
    list_filter = (
        ('ticket_service', admin.RelatedOnlyFieldListFilter),
    )
    list_per_page = 10
    readonly_fields = ('ticket_service', 'ticket_service_event_venue_id', 'event_venue',)

    @queryset_filter('Domain', 'ticket_service__domain__slug')
    def get_queryset(self, request):
        return super(TicketServiceVenueBinderAdmin, self).get_queryset(request)

    def if_scheme_exists(self, obj):
        """Иконка обозначанет, заполнена ли схема зала."""
        from django.contrib.admin.templatetags.admin_list import _boolean_icon

        if obj.scheme != '':
            return _boolean_icon(True)
        else:
            return _boolean_icon(False)
    if_scheme_exists.short_description = _('ticket_service_venue_binder_if_scheme_exists')


class TicketServiceVenueBinderInline(admin.TabularInline):
    model = TicketServiceVenueBinder
    extra = 0
    fields = ('ticket_service', 'ticket_service_event_venue_id', 'ticket_service_event_venue_title', 'event_venue',)
    readonly_fields = ('ticket_service', 'ticket_service_event_venue_id', 'ticket_service_event_venue_title',)

    def has_add_permission(self, request):
        return False


@admin.register(TicketService)
class TicketServiceAdmin(admin.ModelAdmin):
    inlines = (TicketServiceVenueBinderInline, )
    formfield_overrides = {
        TextField: {'widget': JSONEditor},
    }
    prepopulated_fields = {
        'id': ('title',),
    }
    list_display = ('title', 'id', 'is_active',)
    list_per_page = 10

    def get_queryset(self, request):
        return super(TicketServiceAdmin, self).get_queryset(request)
