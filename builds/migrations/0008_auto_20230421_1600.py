# Generated by Django 3.2.18 on 2023-04-21 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builds', '0007_auto_20230307_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='is_public',
            field=models.BooleanField(default=True, help_text='show this build on the site'),
        ),
        migrations.AddField(
            model_name='qcdebuild',
            name='is_public',
            field=models.BooleanField(default=True, help_text='show this build on the site'),
        ),
    ]
