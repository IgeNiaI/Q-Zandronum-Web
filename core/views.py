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
        return self.model.objects.translated()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['builds'] = Build.objects.select_related('platform')
        context['page_config'] = self.get_page_config()
        return context
