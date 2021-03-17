import re
from pathlib import Path
from shutil import disk_usage

from celestia.view_container import ViewContainer, register_view
from chunked_upload.constants import COMPLETE as COMPLETE_CHOICE
from chunked_upload.views import \
    ChunkedUploadCompleteView as DefaultChunkedUploadCompleteView
from chunked_upload.views import ChunkedUploadView
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from builds.models import Build, Platform

from .forms import BuildPreloadedForm
from .models import ChunkedUploadItem

views = ViewContainer()


@register_view(views)
class ChunkedUploadFormView(CreateView):
    template_name = 'builds_upload.html'
    model = Build
    form_class = BuildPreloadedForm
    success_url = reverse_lazy("chunked_upload")
    version_pattern = re.compile(
        r"(?P<version>\d+\.\d+(\.\d+)*(\-)?(b|a|rc|beta|alpha)?(\-)?\d+)",
        flags=re.IGNORECASE
    )

    def get(self, request, *args, **kwargs):
        # WARNING TODO is_ajax is depricated in 3.1, update
        if request.is_ajax():
            return self.get_form_for_upload(request)
        else:
            return super().get(request, *args, **kwargs)

    def get_form_for_upload(self, request):
        """ returns form html snippet for replacement in JSON or
            error message
        """
        upload_id = request.GET.get('upload_id')
        if upload_id:
            # try to fetch a finished upload by id
            try:
                upload_item = ChunkedUploadItem.objects.get(upload_id=upload_id, status=COMPLETE_CHOICE)
            except ChunkedUploadItem.DoesNotExist:
                message = "no finished upload for upload_id provided"
                return JsonResponse({'status': False,
                                     'message': message},
                                    status=404)
            else:
                # return form html snippet with initial value
                initial = self.parse_filename(upload_item.filename)
                initial['upload'] = upload_item
                form = self.form_class(initial=initial)
                return JsonResponse({'status': 'OK',
                                     'form': form.as_p(),
                                     'message': "loaded initialized form"},
                                    status=200)
        else:
            # tell client that required data was not sent
            return JsonResponse({'status': False, 'message': "no upload_id provided"},
                                status=400)
        # this case should never be reached
        return JsonResponse({'status': False, 'message': "unhandled view case (server coding error)"},
                            status=520)

    def parse_filename(self, filename):
        """ try to parse data from the file name for form pre-fill """
        initial = {}
        platforms = Platform.objects.order_by('name').defer('icon_code')
        for platform in platforms:
            if re.search(platform.name, filename, re.IGNORECASE):
                initial['platform'] = platform
                break
        m = re.search(self.version_pattern, filename)
        if m:
            initial['version'] = m.group('version')
        return initial

    def form_valid(self, form):

        build = form.save(commit=False)
        upload_item = form.cleaned_data['upload']
        filename = build.make_filename(upload_item.filename)

        file_moved = False  # flag to revert action
        try:

            with transaction.atomic():
                new_path = Path(settings.MEDIA_ROOT) / filename
                print(f"new path: {new_path}")
                Path(upload_item.file.path).rename(new_path)
                file_moved = True

                build.file = filename

                # try to get existing build for platform and option
                if not form.cleaned_data['create']:
                    old_builds = Build.objects.filter(
                        platform=build.platform,
                        has_doomseeker=build.has_doomseeker
                    ).order_by('version')[:1]
                    if len(old_builds):
                        build.pk = old_builds[0].pk

                build.save()
                upload_item.delete()
            msg = f"Build #{build.pk} '{filename}' saved."
            messages.add_message(self.request, messages.SUCCESS, msg)

        except Exception as exc:
            # cleanup
            if file_moved:
                new_path.rename(upload_item.file.path)
            raise exc

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        """ adds builds for footer and latests uploads """
        context = super().get_context_data(**kwargs)
        builds = Build.objects.select_related('platform').order_by('platform__priority', 'has_doomseeker')
        context['builds'] = builds
        context['disk_usage'] = disk_usage(settings.MEDIA_ROOT)
        context['uploads'] = ChunkedUploadItem.objects.all().order_by('completed_on')[:7]
        return context


@register_view(views)
class ChunkedUploadProcessView(ChunkedUploadView):

    model = ChunkedUploadItem
    field_name = 'the_file'

    def create_chunked_upload(self, save=False, **attrs):
        """
        Creates new chunked upload instance. Called if no 'upload_id' is
        found in the POST data.
        """
        # chunked_upload = self.model(**attrs)
        # file starts empty
        # chunked_upload.file.save(name='', content=ContentFile(''), save=save)
        print(f"create_chunked_upload: {save}")
        return super().create_chunked_upload(save, **attrs)


@register_view(views)
class ChunkedUploadCompleteView(DefaultChunkedUploadCompleteView):

    model = ChunkedUploadItem

    def on_completion(self, uploaded_file, request):
        # Do something with the uploaded file. E.g.:
        # * Store the uploaded file on another model:
        # SomeModel.objects.create(user=request.user, file=uploaded_file)
        # * Pass it as an argument to a function:
        # function_that_process_file(uploaded_file)
        print(f" upload finished: {uploaded_file}")
        pass

    def get_response_data(self, chunked_upload, request):
        return {'message': ("You successfully uploaded '%s' (%s bytes)!" %
                            (chunked_upload.filename, chunked_upload.offset))}
