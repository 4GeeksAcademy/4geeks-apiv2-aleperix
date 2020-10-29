# Generated by Django 3.1.2 on 2020-10-29 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0011_auto_20201006_0058'),
        ('authenticate', '0012_profileacademy'),
    ]

    operations = [
        migrations.AddField(
            model_name='slackteam',
            name='academy',
            field=models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, to='admissions.academy'),
            preserve_default=False,
        ),
    ]
