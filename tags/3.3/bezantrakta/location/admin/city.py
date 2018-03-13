from django.contrib import admin
from django.utils.translation import ugettext as _

from project.cache import cache_factory

from ..forms import CityForm
from ..models import City, Domain


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Админ-панель модели ``City``.

    Attributes:
        form (django.forms.ModelForm): Форма для выбора часовых поясов в выпадающем списке с автозаполнением.
        list_display (tuple): Поля для отображения в списке записей.
        list_per_page (int): Количество объектов на одной странице при пагинации.
        prepopulated_fields (dict): Поля для автозаполнения из значения других полей.
        radio_fields (dict): Поля для выбора с помощью радиокнопок.
        search_fields (tuple): Поля для текстового поиска.
    """
    form = CityForm
    fieldsets = (
        (
            None,
            {
                'fields': ('title', 'slug', 'timezone',),
            }
        ),
        (
            None,
            {
                'fields': ('icon', 'img_preview',),
                'classes': ('help_text',),
                'description': _('city_icon_help_text'),
            }
        ),
    )
    list_display = ('ico_preview', 'title', 'slug', 'timezone_offset', 'state_icons',)
    list_display_links = 'title'
    list_per_page = 10
    prepopulated_fields = {
        'slug': ('title',),
    }
    radio_fields = {'state': admin.VERTICAL, }
    readonly_fields = ('img_preview',)
    search_fields = ('title',)

    def save_model(self, request, obj, form, change):
        """Пересоздать кэш:
        * при сохранении созданной ранее записи,
        * если созданная ранее запись не пересохраняется в новую запись с новым первичным ключом.
        """
        super(CityAdmin, self).save_model(request, obj, form, change)

        # Обновить кэш всех связанных с городом сайтов, если они присутствуют
        city_domains = Domain.objects.filter(city_id=obj.id).values_list('slug', flat=True)
        if city_domains:
            for domain_slug in city_domains:
                cache_factory('domain', domain_slug, reset=True)
