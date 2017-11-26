from django.contrib import admin

from ..forms import CityForm
from ..models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'timezone_offset', 'state_icons',)
    list_per_page = 10
    radio_fields = {'state': admin.VERTICAL, }
    search_fields = ('title',)
