from celestia.translation.admin import TransFormSetMixin
# from django.conf import settings
from django.contrib import admin

from . import models

# from django.forms import BaseModelFormSet

"""
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
    list_display = ('internal_name', 'is_public', 'priority', 'label_is_html')
    inlines = (FeatureTransInline, )


@admin.register(models.Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(models.Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ('platform', 'has_doomseeker', 'version', 'size', 'update_datetime')
    readonly_fields = ('file_datetime', 'create_datetime')
