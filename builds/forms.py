# -*- coding: utf-8 -*-

from chunked_upload.constants import COMPLETE as COMPLETE_CHOICE
from django.forms import ModelChoiceField, ModelForm

from builds.models import Build, ChunkedUploadItem


class BuildPreloadedForm(ModelForm):
    class Meta:
        model = Build
        fields = ['platform', 'has_doomseeker', 'version']

    upload = ModelChoiceField(queryset=ChunkedUploadItem.objects.filter(status=COMPLETE_CHOICE))
