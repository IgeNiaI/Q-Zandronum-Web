# Generated by Django 3.2.18 on 2023-04-21 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bootslider', '0004_auto_20230310_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sliderimage',
            name='preview',
            field=models.ImageField(blank=True, default='', upload_to='public/'),
        ),
    ]
