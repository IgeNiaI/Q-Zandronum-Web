# -*- coding: utf-8 -*-

from celestia.abstract_models import AbstractDateTimeTrackedModel
from celestia.translation.models import (AbstractTranslatedModel,
                                         BaseTranslatedQuerySet)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CoreUser(AbstractUser):
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = "core_user"


class TranslatedPageConfig(AbstractTranslatedModel, AbstractDateTimeTrackedModel):
    class Meta(AbstractTranslatedModel.Meta):
        abstract = False
        verbose_name = _('page configuration translation')
        verbose_name_plural = _('page configuration translations')
        db_table = "core_pageconfig_trans"

    base = models.ForeignKey('PageConfig',
                             on_delete=models.CASCADE,
                             related_name='translations')
    base.help_text = _('a base model of this translation model')

    meta_title = models.CharField(max_length=256)
    meta_title.help_text = _('Page title (shown on the browser tab)')
    meta_descr = models.TextField(blank=True)
    meta_descr.help_text = _('Page description (mostly for search engines)')
    meta_keywords = models.TextField(max_length=1024, blank=True)
    meta_keywords.help_text = _('Keywords for search engines')

    objects = BaseTranslatedQuerySet.as_manager()


class PageConfig(models.Model):
    class Meta:
        verbose_name = _('page configuration')
        verbose_name_plural = _('page configurations')
        db_table = "core_pageconfig"

    page_name = models.SlugField(max_length=64, unique=True)
    page_name.help_text = _('page id for internal use, must contain only a-zA-Z0-9-_')

    def __str__(self):
        return f"{self.page_name} conf"
