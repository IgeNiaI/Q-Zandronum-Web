# -*- coding: utf-8 -*-

from chunked_upload.constants import COMPLETE as COMPLETE_CHOICE
from django.forms import BooleanField, ModelChoiceField, ModelForm

from builds.models import Build, ChunkedUploadItem, QCDEBuild


class BuildPreloadedForm(ModelForm):
    class Meta:
        model = Build
        fields = ['platform', 'has_doomseeker', 'version']

    upload = ModelChoiceField(queryset=ChunkedUploadItem.objects.filter(status=COMPLETE_CHOICE))
    create = BooleanField(required=False, label="Force create",
                          help_text='* Check to create new entry instead of updating one'
                                    ' for same platform')


class QCDEBuildPreloadedForm(BuildPreloadedForm):
    class Meta:
        model = QCDEBuild
        fields = ['platform', 'version']
