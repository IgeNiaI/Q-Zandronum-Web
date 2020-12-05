# -*- coding: utf-8 -*-

from celestia.translation.admin import TransFormSetMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


class PageConfigTransInline(TransFormSetMixin, admin.StackedInline):
    model = models.TranslatedPageConfig
    fields = ('lang_code', 'meta_title', 'meta_descr', 'meta_keywords')


@admin.register(models.CoreUser)
class UserAdo(UserAdmin):
    pass


@admin.register(models.PageConfig)
class PageConfigAdmin(admin.ModelAdmin):
    list_display = ('page_name',)
    inlines = (PageConfigTransInline,)
