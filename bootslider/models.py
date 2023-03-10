import zlib
from pathlib import Path

from celestia.abstract_models import FileProcessingMixin
from celestia.utils.image import make_preview
from django.db import models
from django.forms import Media
from django.utils.html import format_html


class MediaWithInlines(Media):
    """ Media class that handles inlined script and styles """

    def __init__(self, media=None, css=None, js=None, inline_js=None, inline_css=None):
        super().__init__(media=media, css=css, js=js)

        self._css_inlines = [inline_css] if inline_css else []
        self._js_inlines = [inline_js] if inline_js else []

    def render(self):
        safe_str = super().render()

        if self._js_inlines:
            safe_str += format_html("\n<script>{0}</style>", "\n".join(self._js_inlines))
        if self._css_inlines:
            safe_str += format_html("\n<style>{0}</style>", "\n".join(self._css_inlines))
        return safe_str


class AbstractSlider(models.Model):

    class Meta:
        abstract = True

    def _default_attrs():
        return {"data-bs-pause": "false"}

    id = models.SmallAutoField(primary_key=True)

    codename = models.SlugField(max_length=64, unique=True)
    codename.help_text = "Unique identificator and used as html ID"

    slide_select = models.CharField(max_length=128, default='slide-')
    animation_class = models.CharField(max_length=256, default='active')
    ride_class = models.CharField(max_length=256, default='carousel')
    ride_class.help_text = 'class used to init Slider, used in html'

    inline_style = models.TextField(default="", blank=True)
    inline_style.help_text = "added with slider.media, for container style use extra_attrs"

    interval_ms = models.PositiveIntegerField(default=5000)
    interval_ms.help_text = "Slide delay in ms"

    extra_data = models.JSONField(default=_default_attrs, blank=True)
    extra_data.help_text = "html data-* attributes in JSON format"
    extra_attrs = models.JSONField(default=dict, blank=True)
    extra_attrs.help_text = "html attributes in JSON format"

    @property
    def attrs(self):
        all_attrs = {"id": self.codename}
        all_attrs.update(self.extra_attrs)

        css_class = self.ride_class
        if "class" in self.extra_attrs.keys():
            css_class += " " + self.extra_attrs['class']
        print(css_class)
        all_attrs["class"] = css_class

        if self.inline_style:
            all_attrs['style'] = self.inline_style

        all_attrs.update({
            "data-bs-ride": self.ride_class,
            "data-bs-interval": self.interval_ms,
            "data-animation-class": self.animation_class,
            "data-slide-select": self.slide_select,
        })
        all_attrs.update(self.extra_data)
        return " ".join([format_html('{0}="{1}"', key, value) for key, value in all_attrs.items()])

    @property
    def media(self):
        return MediaWithInlines(css={},
                                inline_css=self.inline_style,
                                js=('bs-slider/carousel.js', ))

    def get_path_element(self):
        if self.codename:
            return self.codename
        else:
            raise RuntimeError("Can't use get_path_element() method if instance codename is not set!")

    def __str__(self):
        return self.codename


class SlideQuerySet(models.QuerySet):

    def public(self):
        return self.filter(is_public=True)

    def shuffle(self):
        return self.public().order_by('?')


class AbstractSliderImage(FileProcessingMixin, models.Model):

    class Meta:
        abstract = True

    def make_filename(obj, filename):
        return Path('public/slides/') / obj.slider.get_path_element() / filename

    img_alt = models.CharField(max_length=256, default="img")
    img = models.ImageField(upload_to=make_filename)
    preview = models.ImageField(default='', upload_to='public/', blank=True)

    slider = models.ForeignKey('Slider', related_name='slides', on_delete=models.CASCADE)

    update_dt = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    objects = SlideQuerySet.as_manager()

    crc32 = models.CharField(max_length=8, default='', blank=True)

    # non field attributes
    _file_fields_to_process = {
        'img': {
            'crc32': {'function': zlib.crc32, 'postprocessor': lambda val: f"{val:X}"},
        }
    }
    _file_fields_to_cleanup = ('img', 'preview')
    preview_size = (128, 80)

    def __str__(self):
        return self.img.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.img:
            self.preview = str(make_preview(self.img.path, unlink=True, size=self.preview_size))
            super().save(update_fields=('preview', ), postprocess_files=False)

    def preview_html(self):
        if self.img and self.preview:
            return format_html(
                "<a href='{0}'><img src='{1}' alt='{2}' style='width:{3};height:{4}'></a>",
                self.img.url, self.preview.url, self.img_alt, self.preview_size[0], self.preview_size[1]
            )
        else:
            return "no image"


class Slider(AbstractSlider):
    pass


class SliderImage(AbstractSliderImage):
    pass
