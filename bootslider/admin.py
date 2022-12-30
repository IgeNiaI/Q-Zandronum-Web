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
    list_display = (str, 'id', 'slider', 'is_public')