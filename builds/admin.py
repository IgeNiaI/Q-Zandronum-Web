from celestia.translation.admin import TransFormSetMixin
# from django.conf import settings
from django.contrib import admin
from django.db.models import Count
from django.template import Context, Template
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import models
from .storage import rename_files


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
    upload_url = reverse_lazy("chunked_upload")
    # change_list_template = 'admin/build_change_list.html'

    list_display = ('platform', 'file', 'has_doomseeker', 'version', 'get_total_downloads',
                    'crc32', 'humanize_size', 'update_datetime')
    readonly_fields = ('file_datetime', 'create_datetime', 'upload_link')

    fields = (
        ('file', 'upload_link'),
        'version',
        ('platform', 'has_doomseeker'),
        ('crc32', 'checksum_a'),
        'size',
        ('file_datetime', 'create_datetime'),
    )

    def humanize_size(self, obj):
        return Template("{{ size|filesizeformat }}").render(Context({'size': obj.size}))
    humanize_size.short_description = _('Size')
    humanize_size.admin_order_field = 'size'

    def upload_link(self, obj=None):
        return mark_safe(
            f"<p><a style='padding: 5px 1.5rem;' class='button' href='{self.upload_url}'>"
            "Chunked upload form</a></p>"
            "<p>Use this form to upload large files.</p>"
        )

    def delete_with_files(modeladmin, request, queryset):
        """ run delete on every instance to trigger custom code for
            file cleanup.
        """
        for obj in queryset:
            obj.delete()
    delete_with_files.short_description = _("Delete with files")

    actions = (rename_files, delete_with_files)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate_downloads()


@admin.register(models.QCDEBuild)
class QCDEBuildAdmin(BuildAdmin):
    upload_url = reverse_lazy("qcde_chunked_upload")

    fields = (
        ('file', 'upload_link'),
        'version',
        ('platform'),
        ('crc32', 'checksum_a'),
        'size',
        ('file_datetime', 'create_datetime'),
    )

    list_display = ('platform', 'file', 'version', 'get_total_downloads',
                    'crc32', 'humanize_size', 'update_datetime')


@admin.register(models.WeeklyDownloadCounter)
class DownloadCounterAdmin(admin.ModelAdmin):
    list_display = (str, 'build', 'qcde_build', 'value')
