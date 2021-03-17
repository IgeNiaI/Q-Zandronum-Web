from celestia.translation.admin import TransFormSetMixin
# from django.conf import settings
from django.contrib import admin
from django.db.models import Count
from django.template import Context, Template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import models
from .storage import rename_files

"""
from django.forms import BaseModelFormSet

class TransInlineFormSet(BaseModelFormSet):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 queryset=None, initial=None, **kwargs):
         print(initial)
         super().__init__(data=None, files=None, auto_id='id_%s', prefix=None,
                          queryset=None, initial=None, **kwargs)
         print(self.initial)
         #self.initial = [{'lang_code': i[0]} for i in settings.LANGUAGES]
"""


class FeatureTransInline(TransFormSetMixin, admin.TabularInline):
    model = models.TranslatedFeature
    fields = ('lang_code', 'label_code')


@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    ordering = ('priority', )
    list_display = ('internal_name', 'is_public', 'priority',
                    'available_translations', 'label_is_html', )
    inlines = (FeatureTransInline, )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('translations')
        return qs

    def available_translations(self, obj):
        return ", ".join([x.lang_code for x in obj.translations.all()])

    """
    def icon(self, obj):
        s = f"<div style='max-height: 2rem; max-width: 3rem;'>{ obj.icon_code }</div>"
        return mark_safe(s)
    icon.allow_tags = True
    """


@admin.register(models.Platform)
class PlatformAdmin(admin.ModelAdmin):

    ordering = ('priority', )
    list_display = ('name', 'icon', 'priority', 'build_count')

    def icon(self, obj):
        return mark_safe(obj.icon_code)
    icon.allow_tags = True

    def build_count(self, obj):
        return obj.build_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(build_count=Count('build'))
        return qs

    class Media:
        js = ('https://kit.fontawesome.com/f91e3d92b2.js', )


@admin.register(models.Build)
class BuildAdmin(admin.ModelAdmin):

    list_display = ('platform', 'file', 'has_doomseeker', 'version',
                    'crc32', 'humanize_size', 'update_datetime')
    readonly_fields = ('file_datetime', 'create_datetime')

    def humanize_size(self, obj):
        return Template("{{ size|filesizeformat }}").render(Context({'size': obj.size}))
    humanize_size.short_description = _('Size')
    humanize_size.admin_order_field = 'size'

    def delete_with_files(modeladmin, request, queryset):
        """ run delete on every instance to trigger custom code for
            file cleanup.
        """
        for obj in queryset:
            obj.delete()
    delete_with_files.short_description = _("Delete with files")

    actions = (rename_files, delete_with_files)
