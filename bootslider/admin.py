from django.contrib import admin

from .models import Slider, SliderImage


class ImageInline(admin.TabularInline):
    model = SliderImage
    fields = ('img', 'img_alt')


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('codename', 'id', 'interval_ms')
    inlines = (ImageInline, )

    fields = (
        'codename',
        'ride_class',
        ('slide_select', 'animation_class'),
        'interval_ms',
        'inline_style',
        ('extra_data', 'extra_attrs')
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('slides')
        return qs


@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'preview_html', 'slider', 'is_public')

    list_display_links = ('id', '__str__')

    list_per_page = 25
    search_fields = ('img', 'img_alt')

    actions = ('toggle_public', )

    def toggle_public(self, request, queryset):
        counter = 0
        for img in queryset:
            img.is_public = not img.is_public
            img.save()
        self.message_user(request, f"Toggled public state: {counter}")
