from django.contrib import admin

from adminsortable2.admin import SortableInlineAdminMixin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from ..models import Event, EventCategory, EventContainerBinder, EventLinkBinder, EventGroupBinder


class EventContainerBinderInline(admin.TabularInline):
    model = EventContainerBinder
    extra = 0
    fields = ('event_container', 'order', 'img', 'img_preview',)
    readonly_fields = ('order', 'img_preview',)
    radio_fields = {'event_container': admin.VERTICAL, }


class EventLinkBinderInline(SortableInlineAdminMixin, admin.TabularInline):
    model = EventLinkBinder
    extra = 0
    fields = ('order', 'event_link', 'href', 'img_preview',)
    readonly_fields = ('img_preview',)


class EventGroupBinderInline(admin.TabularInline):
    model = EventGroupBinder
    extra = 0
    fields = ('event_group',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('event_container',)
    inlines = (EventContainerBinderInline, EventLinkBinderInline, EventGroupBinderInline,)
    list_display = ('title', 'date', 'time', 'event_category', 'event_venue',
                    'is_published', 'is_on_index', 'container_count',
                    'link_count', 'domain',)
    list_filter = (
        ('domain', RelatedDropdownFilter),
    )
    list_select_related = ('event_category', 'event_venue', 'domain',)
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {
        'event_category': admin.VERTICAL,
        'min_age': admin.HORIZONTAL,
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'event_category':
            kwargs['queryset'] = EventCategory.objects.filter(is_published=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
