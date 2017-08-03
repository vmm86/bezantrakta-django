from django.contrib import admin
from django.db.models import TextField

from jsoneditor.forms import JSONEditor

from .models import PaymentService


@admin.register(PaymentService)
class PaymentServiceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        TextField: {'widget': JSONEditor},
    }
    prepopulated_fields = {
        'slug': ('title',),
    }
    list_display = ('title', 'slug', 'is_production', )
