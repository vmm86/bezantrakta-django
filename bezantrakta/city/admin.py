from django.contrib import admin
from .models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'city_slug': ('city_title',), }
    list_display = ('city_title', 'city_slug', 'city_status',)
    search_fields = ('city_title',)
