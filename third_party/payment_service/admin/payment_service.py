from django.contrib import admin
from django.db.models import TextField
from django.utils.translation import ugettext as _

from jsoneditor.forms import JSONEditor

from ..cache import payment_service_cache
from ..models import PaymentService


@admin.register(PaymentService)
class PaymentServiceAdmin(admin.ModelAdmin):
    actions = ('batch_set_cache',)

    formfield_overrides = {
        TextField: {'widget': JSONEditor},
    }
    list_display = ('title', 'id', 'is_active', 'is_production',)
    list_per_page = 20

    fieldsets = (
        (
            None,
            {
                'fields': ('title', 'id', 'slug', 'is_active', 'is_production',),
            }
        ),
        (
            None,
            {
                'fields': ('settings',),
                'classes': ('json_settings',),
                'description': _('payment_service_help_text'),
            }
        ),
    )

    prepopulated_fields = {
        'id': ('title',),
    }

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(PaymentServiceAdmin, self).save_model(request, obj, form, change)

        if change and obj._meta.pk.name not in form.changed_data:
            payment_service_cache(obj.id, reset=True)

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for item in queryset:
            payment_service_cache(item.id, reset=True)
    batch_set_cache.short_description = _('payment_service_admin_batch_set_cache')
