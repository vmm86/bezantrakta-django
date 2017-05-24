from django.contrib import admin
from .models import Domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'is_online',)
    search_fields = ('slug', 'title',)
    list_filter = ('city',)
