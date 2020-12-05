from datetime import datetime

from celestia.abstract_models import AbstractDateTimeTrackedModel
from celestia.bleach_models import BleachMixin
from celestia.translation.models import (AbstractTranslatedModel,
                                         BaseTranslatedQuerySet)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Platform(models.Model):
    class Meta:
        verbose_name = _('platform')
        verbose_name_plural = _('platforms')

    name = models.CharField(max_length=64, unique=True)

    icon_code = models.TextField(default="<i>*</i>")

    def __str__(self):
        return self.name


class Build(AbstractDateTimeTrackedModel):
    class Meta:
        verbose_name = _('build')
        verbose_name_plural = _('builds')

        constraints = [
             models.UniqueConstraint(fields=('platform', 'version', 'has_doomseeker'),
                                     name='%(app_label)s_%(class)s_unique_for_pfm_opt_and_ver'),
             # models.UniqueConstraint(fields=('platform', 'checksum_a'),
             # name='%(app_label)s_%(class)s_unique_for_pfm_and_chksum')
        ]

    file = models.FileField(default='test.txt')
    platform = models.ForeignKey('Platform', on_delete=models.PROTECT)

    has_doomseeker = models.BooleanField(default=False)

    size = models.PositiveBigIntegerField(default=0)
    crc32 = models.CharField(max_length=8, blank=True)
    checksum_a = models.CharField(max_length=144, blank=True)

    version = models.CharField(max_length=255)

    file_datetime = models.DateTimeField(
        verbose_name=_('date and time file was changed'),
        default=timezone.make_aware(datetime(2000, 1, 1))
    )

    def __str__(self):
        return f"{self.platform} [{self.version}]"


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

    label_code = models.CharField(max_length=2048)

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

    priority = models.SmallIntegerField(default=200)

    is_public = models.BooleanField(default=False)

    icon_code = models.TextField(default="<i>*</i>")

    label_is_html = models.BooleanField(default=False)

    def __str__(self):
        return self.internal_name
