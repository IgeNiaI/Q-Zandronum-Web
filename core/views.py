# -*- coding: utf-8 -*-

import warnings

from celestia.view_container import ViewContainer, register_view
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
# from django.views.generic import DetailView
from django.views.generic.list import ListView

from builds.models import Build, TranslatedFeature

from .models import TranslatedPageConfig

views = ViewContainer()


class PageConfigMixin:
    page_name = ''

    def get_page_config(self):
        qs = TranslatedPageConfig.objects.translated()
        qs = qs.filter(base__page_name=self.page_name)
        try:
            config = qs.first()
        except TranslatedPageConfig.DoesNotExist:
            warnings.warn(f'PageConfig translation for query "{qs.query}"'
                          f' is not found (page "{self.page_name}")')
            config = None
        return config


@register_view(views)
@method_decorator(gzip_page, name='dispatch')
class IndexView(PageConfigMixin, ListView):
    template_name = 'index.html'
    model = TranslatedFeature
    page_name = 'index'

    def get_queryset(self):
        qs = self.model.objects.translated()
        # NOTE fallback
        if len(qs) == 0:
            qs = self.model.objects.filter(lang_code='en')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        builds = Build.objects.select_related('platform').order_by('platform', 'has_doomseeker')
        context['builds'] = builds
        context['page_config'] = self.get_page_config()
        return context
