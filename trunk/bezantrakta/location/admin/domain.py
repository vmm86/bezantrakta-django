from django.contrib import admin
from django.db.models import TextField
from django.utils.translation import ugettext as _

from jsoneditor.forms import JSONEditor

from project.cache import cache_factory

from bezantrakta.simsim.filters import RelatedOnlyFieldDropdownFilter

from ..models import Domain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """Админ-панель модели ``Domain``.

    Attributes:
        actions (tuple): Пакетные действия для нескольких записей.
        fieldsets (tuple): Группировка полей по секциям в форме редактирования.
        formfield_overrides (dict): Переопределение виджетов для указанных типов полей.
        list_display (tuple): Поля для отображения в списке записей.
        list_filter (tuple): Поля для фильтрации при отображении списка записей.
        list_per_page (int): Количество объектов на одной странице при пагинации.
        list_select_related (tuple): Поля для JOIN-запросов  при отображении списка записей.
        search_fields (tuple): Поля для текстового поиска.
    """
    actions = ('publish_or_unpublish_items', 'batch_set_cache', )
    fieldsets = (
        (
            None,
            {
                'fields': ('id', 'title', 'slug', 'is_published', 'city',),
            }
        ),
        (
            None,
            {
                'fields': ('settings',),
                'classes': ('json_settings',),
                'description': _('domain_settings_help_text'),
            }
        ),
    )
    formfield_overrides = {
        TextField: {'widget': JSONEditor},
    }
    list_display = ('title', 'slug', 'is_published',)
    list_filter = (
        ('city', RelatedOnlyFieldDropdownFilter),
    )
    list_per_page = 10
    list_select_related = ('city',)
    search_fields = ('title', 'slug',)

    def publish_or_unpublish_items(self, request, queryset):
        """Пакетная публикация или снятие с публикации сайтов."""
        for obj in queryset:
            obj.is_published = False if obj.is_published else True
            obj.save(update_fields=['is_published'])

            cache_factory('domain', obj.slug, reset=True)
    publish_or_unpublish_items.short_description = _('domain_admin_publish_or_unpublish_items')

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(DomainAdmin, self).save_model(request, obj, form, change)

        cache_factory('domain', obj.slug, reset=True)

    def batch_set_cache(self, request, queryset):
        """Пакетное пересохранение кэша."""
        for obj in queryset:
            cache_factory('domain', obj.slug, reset=True)
    batch_set_cache.short_description = _('domain_admin_batch_set_cache')
