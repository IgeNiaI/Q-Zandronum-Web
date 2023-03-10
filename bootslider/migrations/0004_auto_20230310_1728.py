# Generated by Django 3.2.17 on 2023-03-10 14:28

from pathlib import Path

from django.conf import settings
from django.db import migrations

PUBLIC_SUBDIR = 'public/'


def move_img(obj, new_path):
    print(f"Changing #{obj.pk} '{obj.img}' to '{new_path}'")
    try:
        Path(obj.img.path).rename(settings.MEDIA_ROOT / new_path)
    except OSError as exc:
        print(f"Couldn't move file: {exc}")

    obj.img = new_path
    obj.save()


def forward(apps, schema_editor):
    SliderImage = apps.get_model("bootslider.SliderImage")
    for obj in SliderImage.objects.exclude(img__startswith=PUBLIC_SUBDIR):
        new_path = f"{PUBLIC_SUBDIR}{obj.img}"
        move_img(obj, new_path)


def revert(apps, schema_editor):
    SliderImage = apps.get_model("bootslider.SliderImage")
    for obj in SliderImage.objects.filter(img__startswith=PUBLIC_SUBDIR):
        new_path = Path(str(obj.img)).relative_to(PUBLIC_SUBDIR)
        move_img(obj, new_path)


class Migration(migrations.Migration):

    dependencies = [
        ('bootslider', '0003_auto_20230101_2028'),
    ]

    operations = [migrations.RunPython(forward, revert)]