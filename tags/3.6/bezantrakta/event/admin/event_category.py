from django.contrib import admin

from ..models import EventCategory


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published',)
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }

    def view_on_site(self, obj):
        return None
