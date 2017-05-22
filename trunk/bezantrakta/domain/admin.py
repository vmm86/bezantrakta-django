from django.contrib import admin
from .models import Domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain_slug', 'domain_title')
    search_fields = ('domain_slug', 'domain_title')
