import hashlib
import zlib
from datetime import datetime, timedelta
from pathlib import Path

from celestia.abstract_models import (AbstractDateTimeTrackedModel,
                                      FileProcessingMixin)
from celestia.bleach_models import BleachMixin
from celestia.translation.models import (AbstractTranslatedModel,
                                         BaseTranslatedQuerySet)
from celestia.utils import split_multiple_ext
from chunked_upload.models import ChunkedUpload
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .storage import BuildOverwriteStorage


def start_of_week_by_day(day=None):
    if day is None:
        day = timezone.now().date()
    start_of_week = day - timedelta(days=day.weekday())
    return start_of_week


class ChunkedUploadItem(ChunkedUpload):
    """ a proxy to default ChunkedUpload """
    class Meta:
        proxy = True

    def __str__(self):
        return f'{self.filename} #{self.upload_id} ({self.get_status_display()})'


class Platform(models.Model):
    """ Target OS platforms """
    class Meta:
        verbose_name = _('platform')
        verbose_name_plural = _('platforms')

    name = models.CharField(max_length=64, unique=True)

    icon_code = models.TextField(default="", blank=True)
    icon_code.help_text = _('not escaped and may contain html')

    priority = models.SmallIntegerField(default=200)
    priority.help_text = _('priority of item when ordering')

    def __str__(self):
        return self.name


class WeeklyDownloadCounterQuerySet(models.QuerySet):
    def for_day(self, build, day=None):
        start_of_week = start_of_week_by_day(day)

        if isinstance(build, Build):
            kwargs = {'build': build}
        elif isinstance(build, QCDEBuild):
            kwargs = {'qcde_build': build}
        else:
            raise ValueError("build argument of 'for_day' must be instance of Build or QCDEBuild!")

        kwargs['start_date'] = start_of_week

        counter, created = self.get_or_create(**kwargs)
        return counter, created

    def increment_for_build(self, build, day=None):
        counter, created = self.for_day(build, day)
        counter.value = models.F('value') + 1
        counter.save(update_fields=['value'])


class WeeklyDownloadCounter(models.Model):

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(build__isnull=False) | models.Q(qcde_build__isnull=False),
                name='both_builds_not_null'
            )
        ]

    value = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    build = models.ForeignKey("Build", blank=True, null=True,
                              related_name='download_counters', on_delete=models.PROTECT)

    qcde_build = models.ForeignKey("QCDEBuild", blank=True, null=True,
                                   related_name='download_counters', on_delete=models.PROTECT)

    objects = WeeklyDownloadCounterQuerySet.as_manager()

    def clean(self):
        if self.build is None and self.qcde_build is None:
            raise ValidationError(_('one of builds for counter must be set'))
        elif self.build and self.qcde_build:
            raise ValidationError(_('only build or qcde_build must be set'))

    def __str__(self):
        return f"{self.start_date} - {self.start_date + timedelta(days=6)}"


class BuildQuerySet(models.QuerySet):
    recent_downloads_filter_kwargs = {'build': models.OuterRef('pk')}

    def public(self, *args, **kwargs):
        if kwargs.get('is_public', True) is not True:
            raise ValueError("public() method of %s can't be called with is_public not being True" % self.__class__.__name__)
        return self.filter(is_public=True, *args, **kwargs)

    def annotate_downloads(self):
        return self.annotate(total_downloads=models.Sum("download_counters__value"))

    def annotate_recent_downloads(self):
        recent = WeeklyDownloadCounter.objects.filter(**self.recent_downloads_filter_kwargs)
        start_of_week = start_of_week_by_day()
        qs = self.annotate(recent_downloads=models.Subquery(
            recent.filter(start_date=start_of_week).values('value'))
        )
        return qs


class QCDEBuildQuerySet(BuildQuerySet):
    recent_downloads_filter_kwargs = {'qcde_build': models.OuterRef('pk')}


class AbstractBuild(FileProcessingMixin, AbstractDateTimeTrackedModel):
    """ Base build model. Implements file related feautures like cheksums and file removal """
    class Meta:
        abstract = True

    _file_fields_to_process = {
        'file': {
            # 'checksum_a':
            # {
            #     'function': hashlib.sha1,
            #     'attr': 'hexdigest',
            #     'postprocessor': lambda val: 'sha1|' + val,  # | is a separator for checksum method
            #     'update_datetime_field': 'file_datetime',
            # },
            'checksum_a':
            {
                'function': '/usr/bin/sha1sum',
                'postprocessor': lambda val: 'sha1|' + val.split(" ")[0].strip(),
                'update_datetime_field': 'file_datetime',
            },
            'crc32': {'function': zlib.crc32, 'postprocessor': lambda val: f"{val:X}"},
            # 'crc32': {'function': '/usr/bin/crc32', 'attr': 'upper'},
            'size': {'function': lambda field: field.size, 'preprocessor': '__field__'}
        }
    }
    _file_fields_to_cleanup = ('file', )

    size = models.PositiveBigIntegerField(default=0)
    size.help_text = _('size in bytes')
    crc32 = models.CharField(max_length=8, blank=True)
    crc32.help_text = _("filled automatically")
    checksum_a = models.CharField(max_length=144, blank=True)
    checksum_a.help_text = _("filled automatically by file upload, supposed to"
                             " use format '<method>|<hexdigest>'")

    version = models.CharField(max_length=255)

    is_public = models.BooleanField(default=True)
    is_public.help_text = _('show this build on the site')

    file_datetime = models.DateTimeField(
        verbose_name=_('date and time file was changed'),
        default=timezone.make_aware(datetime(2000, 1, 1))
    )

    objects = BuildQuerySet.as_manager()

    def get_checksum_a(self, split=True):
        val = self.checksum_a.split('|')  # separator for checksum method
        if split:
            return val
        else:
            return val[-1]

    def delete(self, *args, **kwargs):
        """ remove file before removing instance """
        self.file.delete(save=False)
        return super().delete(*args, **kwargs)

    def get_total_downloads(self):
        """ annotation access method """
        return self.total_downloads
    get_total_downloads.short_description = "total downloads"

    def get_recent_downloads(self):
        """ annotation access method """
        return self.recent_downloads
    get_recent_downloads.short_description = "downloads this week"


class Build(AbstractBuild):
    """ Q-Zandronum build model """
    class Meta:
        verbose_name = _('build')
        verbose_name_plural = _('builds')

        constraints = [
             models.UniqueConstraint(fields=('platform', 'version', 'has_doomseeker'),
                                     name='%(app_label)s_%(class)s_unique_for_pfm_opt_and_ver'),
             # models.UniqueConstraint(fields=('platform', 'checksum_a'),
             # name='%(app_label)s_%(class)s_unique_for_pfm_and_chksum')
        ]

    def make_filename(obj, filename):
        parts = ['Q-Zandronum', obj.version, obj.platform.name]
        path = Path(filename)
        # handle double and multiple extensions like .tar.gz
        multi_tuple = split_multiple_ext(
            path,
            allowed_extensions=settings.CELESTIA_ALLOWED_NESTED_EXTS
        )

        ext = "".join(multi_tuple.subexts) + multi_tuple.ext
        return str(settings.SENDFILE_SUBPATH / (" ".join(parts) + ext))

    file = models.FileField(upload_to=make_filename,
                            storage=BuildOverwriteStorage())
    platform = models.ForeignKey('Platform', on_delete=models.PROTECT)

    has_doomseeker = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.platform} [{self.version}]"

    def get_absolute_url(self):
        if self.has_doomseeker:
            return reverse("build_download_ds", kwargs={"platform": self.platform})
        else:
            return reverse("build_download", kwargs={"platform": self.platform, "build": 'qz'})


class QCDEBuild(AbstractBuild):
    """ QC:DE build model """
    class Meta:
        verbose_name = _('QCDE build')
        verbose_name_plural = _('QCDE builds')

        constraints = [
             models.UniqueConstraint(fields=('platform', 'version'),
                                     name='%(app_label)s_%(class)s_unique_for_pfm_and_ver'),
        ]

    def make_filename(obj, filename):
        return str(settings.SENDFILE_SUBPATH / "qcde/" / filename)

    file = models.FileField(upload_to=make_filename,
                            storage=BuildOverwriteStorage())
    platform = models.ForeignKey('Platform', on_delete=models.PROTECT)

    objects = QCDEBuildQuerySet.as_manager()

    def __str__(self):
        return f"QCDE {self.platform} [{self.version}]"

    def get_absolute_url(self):
        return reverse("build_download", kwargs={"platform": self.platform, "build": 'qcde'})


class TranslatedFeatureQuerySet(BaseTranslatedQuerySet):
    pass


class TranslatedFeature(BleachMixin, AbstractTranslatedModel):  # , AbstractDateTimeTrackedModel):
    class Meta(AbstractTranslatedModel.Meta):
        abstract = False
        verbose_name = _('feature translation')
        verbose_name_plural = _('feature translations')
        db_table = "builds_feature_trans"

    base = models.ForeignKey('Feature',
                             on_delete=models.CASCADE,
                             related_name='translations')
    base.help_text = _('a base model of this translation model')

    label_code = models.CharField(max_length=2048)
    label_code.help_text = _('may contain html, not escaped if base feature has "label_is_html"'
                             ' checked')

    objects = TranslatedFeatureQuerySet.as_manager()

    BLEACH_SHOW_FIELDS = {'label_code': {'tags': ['b', 'i', 'u', 'span', 'p', 'sub']}}

    def cleaned_label(self):
        """ uses implementation of BleachMixin """
        if self.base.label_is_html:
            # bleach and mark string as safe
            return self._bleach_field('label_code')
        else:
            # return as non-safe string and let template engine escape it
            return self.label_code


class Feature(models.Model):
    class Meta:
        verbose_name = _('feature')
        verbose_name_plural = _('features')
        db_table = "builds_feature"

    internal_name = models.CharField(max_length=128, unique=True)
    internal_name.help_text = _('name of feature for internal use. Must be unique.')

    priority = models.SmallIntegerField(default=200)
    priority.help_text = _('priority of item when ordering')

    is_public = models.BooleanField(default=False)
    is_public.help_text = _('show this feature on the site')

    icon_code = models.TextField(default="<i></i>")
    icon_code.help_text = _('not escaped and may contain html')

    label_is_html = models.BooleanField(default=False)
    label_is_html.help_text = _(
        'label requires marking as safe (disable escaping).'
        ' label itself is stored in translation table'
    )

    def __str__(self):
        return self.internal_name
