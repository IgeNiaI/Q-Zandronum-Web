import logging

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils.translation import gettext_lazy as _

# Get an instance of a logger
logger = logging.getLogger('django')


class BuildOverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            abs_path = settings.MEDIA_ROOT / name
            logger.warning(f"File '{abs_path}' exists, will rename it with '.bckp'"
                           " overwriting existing")
            abs_path.rename(abs_path.with_suffix(".bckp"))
        return name


def rename_files(modeladmin, request, queryset):
    """ action function for admin """
    unchanged_counter = 0
    for build in queryset:
        old_name = build.file.name
        new_name = build._meta.model.make_filename(build, build.file.name)
        if old_name != new_name:
            msg = f"Renaming `{old_name}` -> `{new_name}`"
            modeladmin.message_user(request, msg, messages.WARNING)
            old_path = settings.MEDIA_ROOT / build.file.name
            new_path = settings.MEDIA_ROOT / new_name
            try:
                old_path.rename(new_path)
            except Exception as exc:
                msg = f"Couldn't rename {old_name}: {exc}!"
                modeladmin.message_user(request, msg, messages.ERROR)
            else:
                build.file = new_name
                build.save(postprocess_files=False, update_fields=['file'])
        else:
            unchanged_counter += 1
    modeladmin.message_user(request, f"unchanged: {unchanged_counter}", messages.INFO)


rename_files.short_description = _("auto-rename build files")
