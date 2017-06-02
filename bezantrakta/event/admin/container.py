from django.contrib import admin

from ..models import EventContainer
from .container_binder import EventContainerBinderInline


@admin.register(EventContainer)
class EventContainerAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'order', 'is_published',)
    inlines = (EventContainerBinderInline,)
