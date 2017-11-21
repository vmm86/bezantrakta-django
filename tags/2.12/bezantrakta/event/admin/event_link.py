from django.contrib import admin

from project.decorators import queryset_filter
from ..models import EventLink, EventLinkBinder


class EventLinkBinderInline(admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('order', 'event', 'event_datetime_localized', 'href',)
    readonly_fields = ('event', 'event_datetime_localized',)
    template = 'admin/tabular_custom.html'

    @queryset_filter('Domain', 'event__domain__slug')
    def get_queryset(self, request):
        return super(EventLinkBinderInline, self).get_queryset(request)

    def has_add_permission(self, request):
        return False


@admin.register(EventLink)
class EventLinkAdmin(admin.ModelAdmin):
    inlines = (EventLinkBinderInline,)
    list_display = ('title', 'slug', 'img_preview',)
    list_select_related = ()
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
    readonly_fields = ('img_preview',)
