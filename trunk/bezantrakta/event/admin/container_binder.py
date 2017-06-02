from django.contrib import admin

from ..models import EventContainerBinder


class EventContainerBinderInline(admin.StackedInline):
    model = EventContainerBinder
    extra = 1
    # fields = ('event_container', 'order', 'img_preview',)
    # readonly_fields = ('img_preview',)
