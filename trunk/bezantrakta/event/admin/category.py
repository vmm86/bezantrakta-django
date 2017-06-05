from django.contrib import admin

from ..models import EventCategory


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published',)
    prepopulated_fields = {
        'slug': ('title',),
    }
