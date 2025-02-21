# -*- coding: utf-8 -*-

import logging
import warnings

import httpagentparser
from celestia.view_container import ViewContainer, register_view
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from django.views.generic import TemplateView
# from django.views.generic import DetailView
from django.views.generic.list import ListView

from bootslider.models import Slider
from builds.models import Build, QCDEBuild, TranslatedFeature

from .models import TranslatedPageConfig

logger = logging.getLogger("django")
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
def switch_view(request):
    host_requested = request.META['HTTP_HOST'].lower()
    # logger.info(f"HOST: '{host_requested}'")
    if host_requested == "qcde.net" or request.GET.get('force_host_qcde'):
        return QcdeView.as_view()(request)
    else:
        return IndexView.as_view()(request)


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
        builds = Build.objects.select_related('platform').public().order_by('platform__priority', 'has_doomseeker')
        context['builds'] = builds
        context['page_config'] = self.get_page_config()
        return context


@register_view(views)
@method_decorator(gzip_page, name='dispatch')
class QcdeView(PageConfigMixin, TemplateView):
    template_name = 'qcde_index.html'
    page_name = 'qcde_index'

    def get_builds(self, **kwargs):
        return QCDEBuild.objects.select_related('platform').public(**kwargs).order_by('-version')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        win_build = self.get_builds(platform__name="Windows").first()
        lnx_build = self.get_builds(platform__name="Linux amd64").first()

        user_agent = httpagentparser.simple_detect(self.request.META.get("HTTP_USER_AGENT"))
        logger.debug(self.request.META.get("HTTP_USER_AGENT"))
        logger.debug(user_agent)
        if "windows" in user_agent[0].lower():
            context['primary_build'] = win_build
            context['secondary_build'] = lnx_build
        else:
            context['primary_build'] = lnx_build
            context['secondary_build'] = win_build
        logger.debug(f" primary: {context['primary_build']} secondary: {context['secondary_build']} ")

        context['slider'] = Slider.objects.filter(codename='qcde-slider').first()

        context['page_config'] = self.get_page_config()
        return context

@register_view(views)
@method_decorator(gzip_page, name='dispatch')
class GuideView(TemplateView):
    template_name = 'Installing_QCDE_on_Linux.html'
    page_name = "GUIDE"
